export interface Endpoint {
  displayName: string;
  // Model sering endpoint name.
  endpointName: string;
}

export const ENDPOINTS: Endpoint[] = [
  {
    displayName: "Sonnet 4",
    endpointName: "databricks-claude-sonnet-4",
  },
  {
    displayName: "Llama 4 Maverick",
    endpointName: "databricks-llama-4-maverick",
  },
];
