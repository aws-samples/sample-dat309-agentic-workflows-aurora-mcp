import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { DemoStage } from './stage/DemoStage'
import { MeridianDeviceShowcase } from './showcase/MeridianDeviceShowcase'
import './index.css'

/**
 * Lightweight path-based router.
 *
 * We deliberately avoid adding react-router (or any new dep) for the booth
 * demo — each presentation surface is self-contained and the rest of the
 * marketing app is a single-page composition. The `/demo-stage` and `/stage`
 * paths mount the cinematic Demo Stage; `/showcase` and `/device-showcase`
 * mount the device showcase; anything else mounts the existing App.
 *
 * Kiosk loop:           open /demo-stage?kiosk=1
 * Builder (technical):  press B once on the stage, or append ?view=builder
 */
function pickRoot() {
  const path = window.location.pathname.replace(/\/+$/, '')
  if (path === '/demo-stage' || path === '/stage') {
    return <DemoStage />
  }
  if (path === '/showcase' || path === '/device-showcase') {
    return <MeridianDeviceShowcase />
  }
  return <App />
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>{pickRoot()}</React.StrictMode>,
)
