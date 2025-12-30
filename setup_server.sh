#!/bin/bash

# Termux Setup Script for GrowServer (SQLite Edition)
# This script clones the StileDevs/GrowServer repo and modifies it to run on Termux with SQLite.

set -e

REPO_URL="https://github.com/StileDevs/GrowServer.git"
DIR_NAME="GrowServer-Termux"

echo "=== GrowServer Termux Installer ==="
echo "Installing dependencies..."
pkg update -y && pkg upgrade -y
pkg install -y git nodejs python make clang build-essential

if [ -d "$DIR_NAME" ]; then
    echo "Directory $DIR_NAME already exists. Please remove it or rename it."
    exit 1
fi

echo "Cloning repository..."
git clone "$REPO_URL" "$DIR_NAME"
cd "$DIR_NAME"

echo "Modifying files for SQLite..."

# 1. Update packages/db/package.json dependencies
# Use node to reliably edit package.json
node -e "
const fs = require('fs');
const pkgPath = 'packages/db/package.json';
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
delete pkg.dependencies.postgres;
pkg.dependencies['better-sqlite3'] = '^11.1.2';
pkg.dependencies['@types/better-sqlite3'] = '^7.6.11';
fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));
"

# 2. Update packages/db/drizzle.config.ts
cat << 'EOF' > packages/db/drizzle.config.ts
import { defineConfig } from "drizzle-kit";
import { config } from "dotenv";

config({
  path: "../../.env",
});

export default defineConfig({
  dialect: "sqlite",
  schema: "./shared/schemas/index.ts",
  out: "./drizzle",
  dbCredentials: {
    url: "file:./data/data.db",
  },
  strict: false,
  verbose: false,
});
EOF

# 3. Update packages/db/Database.ts
cat << 'EOF' > packages/db/Database.ts
import { drizzle, BetterSqlite3Database } from "drizzle-orm/better-sqlite3";
import DatabaseConstructor from "better-sqlite3";
import fs from "fs";
import path from "path";

import { WorldDB } from "./handlers/World";
import { PlayerDB } from "./handlers/Player";
import { setupSeeds } from "./scripts/seeds";
import { dbPath, dbDir } from "./index";

export class Database {
  public db: BetterSqlite3Database<Record<string, never>>;
  public players;
  public worlds;

  constructor() {
    if (!fs.existsSync(dbDir)) {
      fs.mkdirSync(dbDir, { recursive: true });
    }
    const sqlite = new DatabaseConstructor(dbPath);
    this.db = drizzle(sqlite, { logger: false });

    this.players = new PlayerDB(this.db);
    this.worlds = new WorldDB(this.db);
  }

  public async setup() {
    await setupSeeds();
  }
}
EOF

# 4. Update packages/db/shared/schemas/Player.ts
cat << 'EOF' > packages/db/shared/schemas/Player.ts
import { InferSelectModel, sql } from "drizzle-orm";
import { text, integer, sqliteTable } from "drizzle-orm/sqlite-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";

export const players = sqliteTable("players", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull().unique(),
  display_name: text("display_name").notNull(),
  password: text("password").notNull(),
  role: text("role").notNull(),
  gems: integer("gems").default(0),
  level: integer("level").default(0),
  exp: integer("exp").default(0),
  clothing: text("clothing"),
  inventory: text("inventory"),
  last_visited_worlds: text("last_visited_worlds"),
  created_at: text("created_at").default(sql`(CURRENT_TIMESTAMP)`),
  updated_at: text("updated_at").default(sql`(CURRENT_TIMESTAMP)`),
  heart_monitors: text("heart_monitors").notNull(),
});

export type Players = InferSelectModel<typeof players>;
export const insertUserSchema = createInsertSchema(players);
export const selectUserSchema = createSelectSchema(players);
EOF

# 5. Update packages/db/shared/schemas/World.ts
cat << 'EOF' > packages/db/shared/schemas/World.ts
import { InferSelectModel, sql } from "drizzle-orm";
import { text, integer, sqliteTable } from "drizzle-orm/sqlite-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";

export const worlds = sqliteTable("worlds", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  ownedBy: integer("ownedBy"),
  width: integer("width").notNull(),
  height: integer("height").notNull(),
  blocks: text("blocks"),
  dropped: text("dropped"),
  weather_id: integer("weather_id").default(41),
  created_at: text("created_at").default(sql`(CURRENT_TIMESTAMP)`),
  updated_at: text("updated_at").default(sql`(CURRENT_TIMESTAMP)`),
  worldlock_index: integer("worldlock_index"),
});

export type Worlds = InferSelectModel<typeof worlds>;
export const insertWorldSchema = createInsertSchema(worlds);
export const selectWorldSchema = createSelectSchema(worlds);
EOF

# 6. Update packages/db/handlers/Player.ts
cat << 'EOF' > packages/db/handlers/Player.ts
import { type BetterSqlite3Database } from "drizzle-orm/better-sqlite3";
import { eq, sql, like } from "drizzle-orm";
import { players } from "../shared/schemas/Player";
import bcrypt from "bcryptjs";
import { ROLE } from "@growserver/const";
import { PeerData } from "@growserver/types";

export class PlayerDB {
  constructor(private db: BetterSqlite3Database<Record<string, never>>) {}

  public async get(name: string) {
    const res = await this.db
      .select()
      .from(players)
      .where(like(players.name, name))
      .limit(1)
      .execute();

    if (res.length) return res[0];
    return undefined;
  }

  public async getByUID(userID: number) {
    const res = await this.db
      .select()
      .from(players)
      .where(eq(players.id, userID))
      .limit(1)
      .execute();

    if (res.length) return res[0];
    return undefined;
  }

  public async has(name: string) {
    const res = await this.db
      .select({ count: sql`count(*)` })
      .from(players)
      .where(like(players.name, name))
      .limit(1)
      .execute();

    return (res[0].count as number) > 0;
  }

  public async set(name: string, password: string) {
    const salt = await bcrypt.genSalt(10);
    const hashPassword = await bcrypt.hash(password, salt);

    const res = await this.db
      .insert(players)
      .values({
        display_name: name,
        name: name.toLowerCase(),
        password: hashPassword,
        role: ROLE.BASIC,
        heart_monitors: JSON.stringify({}),
      })
      .returning({ id: players.id });

    if (res.length && res[0].id) return res[0].id;
    return 0;
  }

  public async save(data: PeerData) {
    if (!data.userID) return false;

    const res = await this.db
      .update(players)
      .set({
        name: data.name,
        display_name: data.displayName,
        role: data.role,
        inventory: JSON.stringify(data.inventory),
        clothing: JSON.stringify(data.clothing),
        gems: data.gems,
        level: data.level,
        exp: data.exp,
        last_visited_worlds: JSON.stringify(data.lastVisitedWorlds),
        updated_at: new Date().toISOString().slice(0, 19).replace("T", " "),
        heart_monitors: JSON.stringify(Object.fromEntries(data.heartMonitors)),
      })
      .where(eq(players.id, data.userID))
      .returning({ id: players.id });

    if (res.length) return true;
    else return false;
  }
}
EOF

# 7. Update packages/db/handlers/World.ts
cat << 'EOF' > packages/db/handlers/World.ts
import { type BetterSqlite3Database } from "drizzle-orm/better-sqlite3";
import { eq, sql } from "drizzle-orm";
import { worlds } from "../shared/schemas/World";
import { WorldData } from "@growserver/types";

export class WorldDB {
  constructor(private db: BetterSqlite3Database<Record<string, never>>) {}

  public async get(name: string) {
    const res = await this.db
      .select()
      .from(worlds)
      .where(eq(worlds.name, name))
      .limit(1)
      .execute();

    if (res.length) return res[0];
    return undefined;
  }

  public async has(name: string) {
    const res = await this.db
      .select({ count: sql`count(*)` })
      .from(worlds)
      .where(eq(worlds.name, name))
      .limit(1)
      .execute();

    return (res[0].count as number) > 0;
  }

  public async set(data: WorldData) {
    if (!data.name && !data.blocks && !data.width && !data.height) return 0;

    const worldLockData = data.worldLockIndex
      ? data.blocks[data.worldLockIndex].lock
      : null;

    const res = await this.db
      .insert(worlds)
      .values({
        name: data.name,
        ownedBy: worldLockData?.ownerUserID ?? null,
        width: data.width,
        height: data.height,
        blocks: JSON.stringify(data.blocks),
        dropped: JSON.stringify(data.dropped),
        updated_at: new Date().toISOString().slice(0, 19).replace("T", " "),
        weather_id: data.weather.id,
        worldlock_index: data.worldLockIndex,
      })
      .returning({ id: worlds.id });

    if (res.length && res[0].id) return res[0].id;
    return 0;
  }

  public async save(data: WorldData) {
    if (!data.name && !data.blocks && !data.width && !data.height) return false;

    const worldLockData = data.worldLockIndex
      ? data.blocks[data.worldLockIndex].lock
      : null;

    const res = await this.db
      .update(worlds)
      .set({
        ownedBy: worldLockData?.ownerUserID ?? null,
        width: data.width,
        height: data.height,
        blocks: JSON.stringify(data.blocks),
        dropped: JSON.stringify(data.dropped),
        updated_at: new Date().toISOString().slice(0, 19).replace("T", " "),
        weather_id: data.weather.id,
      })
      .where(eq(worlds.name, data.name))
      .returning({ id: worlds.id });

    if (res.length) return true;
    return false;
  }
}
EOF

# 8. Create .env
echo "DATABASE_URL=file:./data/data.db" > .env
echo "PORT=17091" >> .env
echo "ENET_Use_Compression=true" >> .env
echo "ENET_Use_Checksum=true" >> .env

# 9. Handle items.dat (Check parent directory)
if [ -f "../items.dat" ]; then
    echo "Found items.dat in parent directory. Copying..."
    mkdir -p apps/server/assets
    cp "../items.dat" apps/server/assets/items.dat
else
    echo "WARNING: items.dat not found in parent directory."
    echo "Please place items.dat in apps/server/assets/ manually."
fi

echo "Files modified successfully."
echo "Installing NPM dependencies..."

# Use pnpm if available, else install it
if ! command -v pnpm &> /dev/null; then
    npm install -g pnpm
fi

pnpm install

echo "Building the project..."
pnpm build

echo "Setup Complete!"
echo "To start the server, run: cd $DIR_NAME && npm start"
