import type { Changes, MixConfig } from '../types';

/** Apply backend instructions without mutating the user's current configuration. */
export function applyChanges(config: MixConfig, changes: Changes): MixConfig {
  const remaining = config.accessoryCodes.filter(code => !changes.removeAccessories?.includes(code));
  return {
    ...config,
    colorCode: changes.colorCode ?? config.colorCode,
    styleCode: changes.styleCode ?? config.styleCode,
    accessoryCodes: [...new Set([...remaining, ...(changes.addAccessories || [])])],
  };
}
