import { betterAuth } from "better-auth";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL!,
  },
  plugins: [],
});
