CREATE SCHEMA IF NOT EXISTS "public";
CREATE SCHEMA IF NOT EXISTS "auth";
CREATE SCHEMA IF NOT EXISTS "neon_auth";
CREATE SCHEMA IF NOT EXISTS "pgrst";

CREATE TABLE IF NOT EXISTS "users" (
	"id" bigserial PRIMARY KEY,
	"username" text NOT NULL UNIQUE,
	"name" text NOT NULL,
	"email" text NOT NULL UNIQUE,
	"role" text DEFAULT 'user' NOT NULL,
	"is_active" boolean DEFAULT true NOT NULL,
	"password_hash" text DEFAULT 'password' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"avatar" text,
	"pla_pagament" text,
	CONSTRAINT "users_role_check" CHECK (role IN ('admin', 'support', 'user'))
);

CREATE TABLE IF NOT EXISTS "pelicules" (
	"id" integer PRIMARY KEY,
	"user_id" integer,
	"title" text,
	"description" text,
	"video_url" text,
	"poster_path" text,
	"backdrop_url" text,
	"duration" integer,
	"file_size" integer,
	"is_public" boolean,
	"categoria" json,
	"reparto" json,
	"direccio" json,
	"fecha_estreno" timestamp
);

CREATE TABLE IF NOT EXISTS "videos" (
	"id" bigserial PRIMARY KEY,
	"user_id" bigint NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"video_url" text NOT NULL,
	"thumbnail_url" text,
	"duration" integer,
	"file_size" bigint,
	"is_public" boolean DEFAULT false NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"categoria" text,
	"reparto" text,
	"direccio" text,
	"calificacio" integer,
	"fecha_estreno" date,
	CONSTRAINT "fk_videos_user_id" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE
);

-- Neon Auth Tables
CREATE TABLE IF NOT EXISTS "neon_auth"."user" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" text NOT NULL,
	"email" text NOT NULL UNIQUE,
	"emailVerified" boolean NOT NULL,
	"image" text,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updatedAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"role" text,
	"banned" boolean,
	"banReason" text,
	"banExpires" timestamp with time zone
);

CREATE TABLE IF NOT EXISTS "neon_auth"."account" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"accountId" text NOT NULL,
	"providerId" text NOT NULL,
	"userId" uuid NOT NULL REFERENCES "neon_auth"."user"("id") ON DELETE CASCADE,
	"accessToken" text,
	"refreshToken" text,
	"idToken" text,
	"accessTokenExpiresAt" timestamp with time zone,
	"refreshTokenExpiresAt" timestamp with time zone,
	"scope" text,
	"password" text,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updatedAt" timestamp with time zone NOT NULL
);

CREATE TABLE IF NOT EXISTS "neon_auth"."session" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"expiresAt" timestamp with time zone NOT NULL,
	"token" text NOT NULL UNIQUE,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updatedAt" timestamp with time zone NOT NULL,
	"ipAddress" text,
	"userAgent" text,
	"userId" uuid NOT NULL REFERENCES "neon_auth"."user"("id") ON DELETE CASCADE,
	"impersonatedBy" text,
	"activeOrganizationId" text
);

CREATE TABLE IF NOT EXISTS "neon_auth"."organization" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" text NOT NULL,
	"slug" text NOT NULL UNIQUE,
	"logo" text,
	"createdAt" timestamp with time zone NOT NULL,
	"metadata" text
);

CREATE TABLE IF NOT EXISTS "neon_auth"."member" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"organizationId" uuid NOT NULL REFERENCES "neon_auth"."organization"("id") ON DELETE CASCADE,
	"userId" uuid NOT NULL REFERENCES "neon_auth"."user"("id") ON DELETE CASCADE,
	"role" text NOT NULL,
	"createdAt" timestamp with time zone NOT NULL
);

CREATE TABLE IF NOT EXISTS "neon_auth"."invitation" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"organizationId" uuid NOT NULL REFERENCES "neon_auth"."organization"("id") ON DELETE CASCADE,
	"email" text NOT NULL,
	"role" text,
	"status" text NOT NULL,
	"expiresAt" timestamp with time zone NOT NULL,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"inviterId" uuid NOT NULL REFERENCES "neon_auth"."user"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "neon_auth"."jwks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"publicKey" text NOT NULL,
	"privateKey" text NOT NULL,
	"createdAt" timestamp with time zone NOT NULL,
	"expiresAt" timestamp with time zone
);

CREATE TABLE IF NOT EXISTS "neon_auth"."verification" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"identifier" text NOT NULL,
	"value" text NOT NULL,
	"expiresAt" timestamp with time zone NOT NULL,
	"createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updatedAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "neon_auth"."project_config" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" text NOT NULL,
	"endpoint_id" text NOT NULL UNIQUE,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"trusted_origins" jsonb NOT NULL,
	"social_providers" jsonb NOT NULL,
	"email_provider" jsonb,
	"email_and_password" jsonb,
	"allow_localhost" boolean NOT NULL,
	"plugin_configs" jsonb,
	"webhook_config" jsonb
);

-- Indices are already handled by primary/unique keys in CREATE TABLE.
-- But we can add the explicit ones if needed.
CREATE INDEX IF NOT EXISTS "idx_videos_user_id" ON "videos" ("user_id");
