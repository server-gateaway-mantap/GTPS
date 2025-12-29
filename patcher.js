const fs = require('fs');
const path = require('path');

console.log('Applying Termux patches...');

// Helper
function writeFile(filePath, content) {
    const p = path.resolve(filePath);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, content);
    console.log(`Updated ${filePath}`);
}

// 1. Modify packages/db/package.json
try {
    const pkgPath = 'packages/db/package.json';
    if (fs.existsSync(pkgPath)) {
        const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

        // Remove Postgres
        if (pkg.dependencies) delete pkg.dependencies['postgres'];

        // Add SQLite
        pkg.dependencies = pkg.dependencies || {};
        pkg.dependencies['better-sqlite3'] = '^11.0.0'; // Latest stable

        pkg.devDependencies = pkg.devDependencies || {};
        pkg.devDependencies['@types/better-sqlite3'] = '^7.6.0';

        fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));
        console.log('Updated packages/db/package.json');
    }
} catch (e) {
    console.error('Failed to update package.json', e);
}

// 2. Overwrite Schemas
const playerSchema = `import { InferSelectModel, sql } from "drizzle-orm";
import { text, integer, sqliteTable } from "drizzle-orm/sqlite-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";

export const players = sqliteTable("players", {
  id: integer("id", { mode: "number" }).primaryKey({ autoIncrement: true }),
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
  created_at: text("created_at").default(sql`(current_timestamp)`),
  updated_at: text("updated_at").default(sql`(current_timestamp)`),
  heart_monitors: text("heart_monitors").notNull(),
});

export type Players = InferSelectModel<typeof players>;
export const insertUserSchema = createInsertSchema(players);
export const selectUserSchema = createSelectSchema(players);
`;

const worldSchema = `import { InferSelectModel, sql } from "drizzle-orm";
import { text, integer, sqliteTable } from "drizzle-orm/sqlite-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";

export const worlds = sqliteTable("worlds", {
  id: integer("id", { mode: "number" }).primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  ownedBy: integer("ownedBy"),
  width: integer("width").notNull(),
  height: integer("height").notNull(),
  blocks: text("blocks"),
  dropped: text("dropped"),
  weather_id: integer("weather_id").default(41),
  created_at: text("created_at").default(sql`(current_timestamp)`),
  updated_at: text("updated_at").default(sql`(current_timestamp)`),
  worldlock_index: integer("worldlock_index"),
});

export type Worlds = InferSelectModel<typeof worlds>;
export const insertWorldSchema = createInsertSchema(worlds);
export const selectWorldSchema = createSelectSchema(worlds);
`;

writeFile('packages/db/shared/schemas/Player.ts', playerSchema);
writeFile('packages/db/shared/schemas/World.ts', worldSchema);

// 3. Update Database.ts
const databaseTs = `import { drizzle, type BetterSQLite3Database } from "drizzle-orm/better-sqlite3";
import DatabaseConstructor from "better-sqlite3";
import path from "path";

import { WorldDB } from "./handlers/World";
import { PlayerDB } from "./handlers/Player";
import { setupSeeds } from "./scripts/seeds";

export class Database {
  public db: BetterSQLite3Database<Record<string, never>>;
  public players;
  public worlds;

  constructor() {
    // Database stored in packages/db/data/database.db
    // Handle both dev (ts-node) and prod (dist) paths
    const dbRoot = __dirname.includes('dist') ? path.resolve(__dirname, '..') : __dirname;
    const dbPath = path.resolve(dbRoot, "data/database.db");

    // Ensure directory exists
    const fs = require('fs');
    if (!fs.existsSync(path.dirname(dbPath))) {
      fs.mkdirSync(path.dirname(dbPath), { recursive: true });
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
`;
writeFile('packages/db/Database.ts', databaseTs);

// 4. Update Handlers
const playerHandler = `import { type BetterSQLite3Database } from "drizzle-orm/better-sqlite3";
import { eq, sql, like } from "drizzle-orm";
import { players } from "../shared/schemas/Player";
import bcrypt from "bcryptjs";
import { ROLE } from "@growserver/const";
import { PeerData } from "@growserver/types";

export class PlayerDB {
  constructor(private db: BetterSQLite3Database<Record<string, never>>) {}

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
`;

const worldHandler = `import { type BetterSQLite3Database } from "drizzle-orm/better-sqlite3";
import { eq, sql } from "drizzle-orm";
import { worlds } from "../shared/schemas/World";
import { WorldData } from "@growserver/types";

export class WorldDB {
  constructor(private db: BetterSQLite3Database<Record<string, never>>) {}

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
`;
writeFile('packages/db/handlers/Player.ts', playerHandler);
writeFile('packages/db/handlers/World.ts', worldHandler);

// 5. Update Seeds
const seedsTs = `"use strict";

import { players } from "../";
import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import bcrypt from "bcryptjs";
import path from "path";

async function hash(password) {
  const salt = await bcrypt.genSalt(10);
  return await bcrypt.hash(password, salt);
}

export async function setupSeeds() {
  // seeds.ts is in packages/db/scripts/ or packages/db/dist/scripts/
  // We want packages/db/data/database.db
  const scriptRoot = __dirname.includes('dist') ? path.resolve(__dirname, '../..') : path.resolve(__dirname, '..');
  const dbPath = path.resolve(scriptRoot, "data/database.db");

  // Ensure directory exists
  const fs = require('fs');
  if (!fs.existsSync(path.dirname(dbPath))) {
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
  }

  const sqlite = new Database(dbPath);
  const db = drizzle(sqlite);
  const dateNow = new Date().toISOString().slice(0, 19).replace("T", " ");

  // Drop and recreate table if it exists
  sqlite.exec(\`DROP TABLE IF EXISTS players;\`);
  sqlite.exec(\`
    CREATE TABLE IF NOT EXISTS players (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      display_name TEXT NOT NULL,
      password TEXT NOT NULL,
      role TEXT NOT NULL,
      gems INTEGER DEFAULT 0,
      level INTEGER DEFAULT 0,
      exp INTEGER DEFAULT 0,
      clothing TEXT,
      inventory TEXT,
      last_visited_worlds TEXT,
      created_at TEXT DEFAULT (current_timestamp),
      updated_at TEXT DEFAULT (current_timestamp),
      heart_monitors TEXT NOT NULL
    );
  \`);

  sqlite.exec(\`
    CREATE TABLE IF NOT EXISTS worlds (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      ownedBy INTEGER,
      width INTEGER NOT NULL,
      height INTEGER NOT NULL,
      blocks TEXT,
      dropped TEXT,
      weather_id INTEGER DEFAULT 41,
      created_at TEXT DEFAULT (current_timestamp),
      updated_at TEXT DEFAULT (current_timestamp),
      worldlock_index INTEGER
    );
  \`);

  // Basic User Seeds
  db.insert(players)
    .values([
      {
        name: "admin",
        display_name: "admin",
        password: await hash("admin"),
        role: "1",
        gems: 1000,
        clothing: null,
        inventory: null,
        last_visited_worlds: null,
        created_at: dateNow,
        heart_monitors: JSON.stringify({}),
      },
      {
        name: "reimu",
        display_name: "Reimu",
        password: await hash("hakurei"),
        role: "2",
        gems: 1000,
        clothing: null,
        inventory: null,
        last_visited_worlds: null,
        created_at: dateNow,
        heart_monitors: JSON.stringify({}),
      },
    ])
    .onConflictDoNothing()
    .run();
}
`;
writeFile('packages/db/scripts/seeds.ts', seedsTs);

// 6. Update Configs
const drizzleConfig = `import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "sqlite",
  schema: ["./shared/schemas/index.ts"],
  out: "./drizzle",
  dbCredentials: {
    url: "data/database.db",
  },
  strict: false,
  verbose: false,
});
`;

const serverDrizzleConfig = `import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "sqlite",
  schema: ["../../packages/db/shared/schemas/index.ts"],
  out: "./drizzle",
  dbCredentials: {
    url: "../../packages/db/data/database.db",
  },
  strict: false,
  verbose: false,
});
`;

writeFile('packages/db/drizzle.config.ts', drizzleConfig);
writeFile('apps/server/drizzle.config.ts', serverDrizzleConfig);

console.log('Patches applied successfully.');
