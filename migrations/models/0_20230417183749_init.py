from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "telegram_user_id" BIGINT NOT NULL UNIQUE,
    "wait_answer_for" TEXT,
    "selected_work_date" DATE,
    "timezone" VARCHAR(20) NOT NULL  DEFAULT 'UTC'
);
CREATE TABLE IF NOT EXISTS "task" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "position" INT NOT NULL,
    "reward" INT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "owner_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
ALTER TABLE "task" DROP CONSTRAINT IF EXISTS "ut_idx_task_owner_i_63c12d";ALTER TABLE "task" ADD CONSTRAINT "ut_idx_task_owner_i_63c12d" UNIQUE ("owner_id", "position") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "task" DROP CONSTRAINT IF EXISTS "ut_idx_task_owner_i_47cd8a";ALTER TABLE "task" ADD CONSTRAINT "ut_idx_task_owner_i_47cd8a" UNIQUE ("owner_id", "name") DEFERRABLE INITIALLY IMMEDIATE;
CREATE TABLE IF NOT EXISTS "worklog" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(20) NOT NULL  DEFAULT 'user_work',
    "name" TEXT NOT NULL,
    "date" DATE NOT NULL,
    "reward" INT NOT NULL,
    "owner_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "task_id" BIGINT REFERENCES "task" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_worklog_owner_i_4e7f9a" ON "worklog" USING BRIN ("owner_id", "date");
CREATE INDEX IF NOT EXISTS "idx_worklog_task_id_c3e84d" ON "worklog" USING BRIN ("task_id", "date");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
