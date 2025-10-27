/// <reference path="../.astro/types.d.ts" />
/// <reference types="astro/client" />

interface ImportMetaEnv {
  readonly BACKEND_URL?: string;
  readonly PUBLIC_BACKEND_URL?: string;
  readonly BACKEND_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
