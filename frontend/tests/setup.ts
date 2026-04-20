import { vi } from 'vitest'

vi.mock('@amap/amap-jsapi-loader', () => ({
  default: {
    load: vi.fn().mockResolvedValue({}),
  },
}))
