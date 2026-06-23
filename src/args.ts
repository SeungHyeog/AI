export function awsRegionArgs(region: string): readonly string[] {
  return ["--region", region, "--output", "json"]
}

export function kubectlContextArgs(cluster: string): readonly string[] {
  return ["--context", cluster]
}

export function namespaceArgs(namespace: string | undefined): readonly string[] {
  return namespace === undefined ? [] : ["--namespace", namespace]
}

export function keyValueSetArgs(values: Readonly<Record<string, string | number | boolean>>): readonly string[] {
  return Object.entries(values).flatMap(([key, value]) => ["--set", `${key}=${String(value)}`])
}
