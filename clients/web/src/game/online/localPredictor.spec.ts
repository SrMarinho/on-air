import { describe, expect, it } from 'vitest'
import { SIMULATION_DT } from '@/game/engine/physics'
import { LocalPredictor } from './localPredictor'

const floor = [{ x: 0, y: 100, w: 1000, h: 32 }]
const right = { left: false, right: true, jump: false }

describe('LocalPredictor', () => {
  it('replays unacknowledged inputs on top of the server state', () => {
    const predictor = new LocalPredictor()
    predictor.start(1, 0, 65)
    for (let i = 0; i < 10; i++) predictor.step(right, floor, SIMULATION_DT)
    const predictedX = predictor.body!.x

    // Server confirmed the first 5 inputs and agrees with the prediction so far.
    const shadow = new LocalPredictor()
    shadow.start(1, 0, 65)
    for (let i = 0; i < 5; i++) shadow.step(right, floor, SIMULATION_DT)
    predictor.reconcile(shadow.body!, 5, floor, SIMULATION_DT)

    expect(predictor.body!.x).toBeCloseTo(predictedX, 3)
  })

  it('snaps when the server disagrees by a lot', () => {
    const predictor = new LocalPredictor()
    predictor.start(1, 0, 65)
    predictor.step(right, floor, SIMULATION_DT)

    predictor.reconcile({ x: 500, y: 65, vx: 0, vy: 0 }, 1, floor, SIMULATION_DT)

    expect(predictor.renderPosition(0)?.x).toBe(500)
  })
})
