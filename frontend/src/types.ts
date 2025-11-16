export interface Site {
  id: string;
  domain: string;
  ssl: boolean;
  ssl_provider: string;
  proxy_pass: string;
  proxy_headers: Record<string, string>;
}

export interface SitePayload {
  domain: string;
  ssl: boolean;
  ssl_provider: string;
  proxy_pass: string;
  proxy_headers: Record<string, string>;
}

