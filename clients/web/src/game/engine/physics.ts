import { world } from '@/design/tokens'
import { approach, overlaps, type Rect } from './geometry'

/** Mirrors backend `PhysicsConfig`. Keep both in sync: prediction depends on it. */
export const PHYSICS = {
  gravity: 2200,
  maxFallSpeed: 900,
  runSpeed: 260,
  groundAccel: 3000,
  airAccel: 1800,
  jumpSpeed: 720,
  jumpReleaseSpeed: 300,
  coyoteTime: 0.1,
  jumpBufferTime: 0.12,
  wallSlideSpeed: 180,
  wallJumpPush: 320,
  playerWidth: world.character.hitboxW,
  playerHeight: world.character.hitboxH,
} as const

export const SIMULATION_DT = 1 / 60

export interface PlayerInputState {
  left: boolean
  right: boolean
  jump: boolean
}

export interface Solid extends Rect {
  vx?: number
  vy?: number
}

export interface PlayerBody {
  x: number
  y: number
  vx: number
  vy: number
  onGround: boolean
  wallLeft: boolean
  wallRight: boolean
  ground: Solid | null
  coyoteTimeLeft: number
  jumpBufferLeft: number
  previousJump: boolean
}

export function createBody(x: number, y: number): PlayerBody {
  return {
    x,
    y,
    vx: 0,
    vy: 0,
    onGround: false,
    wallLeft: false,
    wallRight: false,
    ground: null,
    coyoteTimeLeft: 0,
    jumpBufferLeft: 0,
    previousJump: false,
  }
}

/** One fixed step for a single player, same order as the server scheduler. */
export function stepPlayer(
  body: PlayerBody,
  input: PlayerInputState,
  solids: readonly Solid[],
  dt: number = SIMULATION_DT,
): void {
  applyGravity(body, dt)
  applyControl(body, input, dt)
  moveAndCollide(body, solids, dt)
}

function applyGravity(body: PlayerBody, dt: number): void {
  body.vy = Math.min(body.vy + PHYSICS.gravity * dt, PHYSICS.maxFallSpeed)
}

function applyControl(body: PlayerBody, input: PlayerInputState, dt: number): void {
  const direction = Number(input.right) - Number(input.left)
  const accel = body.onGround ? PHYSICS.groundAccel : PHYSICS.airAccel
  body.vx = approach(body.vx, direction * PHYSICS.runSpeed, accel * dt)

  body.jumpBufferLeft =
    input.jump && !body.previousJump ? PHYSICS.jumpBufferTime : Math.max(0, body.jumpBufferLeft - dt)
  body.previousJump = input.jump

  const touchingWall = body.wallLeft || body.wallRight
  if (body.jumpBufferLeft > 0) {
    if (body.onGround || body.coyoteTimeLeft > 0) {
      body.vy = -PHYSICS.jumpSpeed
      body.jumpBufferLeft = 0
      body.coyoteTimeLeft = 0
    } else if (touchingWall) {
      body.vy = -PHYSICS.jumpSpeed
      body.vx = (body.wallLeft ? 1 : -1) * PHYSICS.wallJumpPush
      body.jumpBufferLeft = 0
    }
  }

  if (!input.jump && body.vy < -PHYSICS.jumpReleaseSpeed) body.vy = -PHYSICS.jumpReleaseSpeed

  const pressingWall = (body.wallLeft && direction < 0) || (body.wallRight && direction > 0)
  if (pressingWall && !body.onGround && body.vy > PHYSICS.wallSlideSpeed) {
    body.vy = PHYSICS.wallSlideSpeed
  }
}

function moveAndCollide(body: PlayerBody, solids: readonly Solid[], dt: number): void {
  const w = PHYSICS.playerWidth
  const h = PHYSICS.playerHeight
  const carryX = (body.ground?.vx ?? 0) * dt
  const carryY = (body.ground?.vy ?? 0) * dt

  body.x += body.vx * dt + carryX
  body.wallLeft = body.wallRight = false
  for (const solid of solids) {
    if (!overlaps({ x: body.x, y: body.y, w, h }, solid)) continue
    if (body.vx > 0 || carryX > 0) {
      body.x = solid.x - w
      body.wallRight = true
    } else {
      body.x = solid.x + solid.w
      body.wallLeft = true
    }
    body.vx = 0
  }

  body.y += body.vy * dt + carryY
  body.onGround = false
  body.ground = null
  for (const solid of solids) {
    if (!overlaps({ x: body.x, y: body.y, w, h }, solid)) continue
    if (body.vy >= 0) {
      body.y = solid.y - h
      body.onGround = true
      body.ground = solid
    } else {
      body.y = solid.y + solid.h
    }
    body.vy = 0
  }

  body.coyoteTimeLeft = body.onGround ? PHYSICS.coyoteTime : Math.max(0, body.coyoteTimeLeft - dt)
}
