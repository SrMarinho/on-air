import { onBeforeUnmount, onMounted, ref, type Ref } from 'vue'

/** `performance.now()` refreshed every `intervalMs`, for countdowns in templates. */
export function useNow(intervalMs = 250): Ref<number> {
  const now = ref(performance.now())
  let timer: number | undefined
  onMounted(() => (timer = window.setInterval(() => (now.value = performance.now()), intervalMs)))
  onBeforeUnmount(() => window.clearInterval(timer))
  return now
}
