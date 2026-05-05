import { Suspense, lazy, useRef, useState, useCallback, useEffect } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'

const Spline = lazy(() => import('@splinetool/react-spline'))

function SpotlightCursor() {
  const containerRef = useRef(null)
  const [isHovered, setIsHovered] = useState(false)
  const [parent, setParent] = useState(null)
  const size = 480

  const mouseX = useSpring(0, { bounce: 0 })
  const mouseY = useSpring(0, { bounce: 0 })
  const left = useTransform(mouseX, x => `${x - size / 2}px`)
  const top  = useTransform(mouseY, y => `${y - size / 2}px`)

  useEffect(() => {
    if (containerRef.current) {
      const p = containerRef.current.parentElement
      if (p) setParent(p)
    }
  }, [])

  const onMove = useCallback((e) => {
    if (!parent) return
    const { left: l, top: t } = parent.getBoundingClientRect()
    mouseX.set(e.clientX - l)
    mouseY.set(e.clientY - t)
  }, [parent, mouseX, mouseY])

  useEffect(() => {
    if (!parent) return
    const onEnter = () => setIsHovered(true)
    const onLeave = () => setIsHovered(false)
    parent.addEventListener('mousemove', onMove)
    parent.addEventListener('mouseenter', onEnter)
    parent.addEventListener('mouseleave', onLeave)
    return () => {
      parent.removeEventListener('mousemove', onMove)
      parent.removeEventListener('mouseenter', onEnter)
      parent.removeEventListener('mouseleave', onLeave)
    }
  }, [parent, onMove])

  return (
    <motion.div
      ref={containerRef}
      style={{
        position: 'absolute',
        width: size,
        height: size,
        left,
        top,
        borderRadius: '50%',
        background: 'radial-gradient(circle at center, rgba(16,163,127,0.15) 0%, rgba(16,163,127,0.05) 50%, transparent 80%)',
        filter: 'blur(40px)',
        pointerEvents: 'none',
        zIndex: 10,
        opacity: isHovered ? 1 : 0,
        transition: 'opacity 0.3s ease',
      }}
    />
  )
}

export default function AnimatedBackground() {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 0, background: '#080810', overflow: 'hidden' }}>

      {/* Gradient base */}
      <div style={{
        position: 'absolute', inset: 0, zIndex: 1, pointerEvents: 'none',
        background: `
          radial-gradient(ellipse 65% 55% at 15% 15%, rgba(16,163,127,0.13) 0%, transparent 65%),
          radial-gradient(ellipse 55% 45% at 85% 80%, rgba(59,130,246,0.09) 0%, transparent 60%),
          radial-gradient(ellipse 45% 35% at 55% 5%,  rgba(139,92,246,0.06) 0%, transparent 55%)
        `,
      }} />

      {/* Spline 3D scene */}
      <div style={{ position: 'absolute', inset: 0, zIndex: 2, opacity: 0.9 }}>
        <Suspense fallback={null}>
          <Spline
            scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
            style={{ width: '100%', height: '100%' }}
          />
        </Suspense>
      </div>

      {/* Mouse spotlight */}
      <SpotlightCursor />

      {/* Readability vignette */}
      <div style={{
        position: 'absolute', inset: 0, zIndex: 11, pointerEvents: 'none',
        background: `
          radial-gradient(ellipse 70% 100% at 50% 50%, transparent 25%, rgba(8,8,16,0.6) 100%),
          linear-gradient(to bottom, rgba(8,8,16,0.25) 0%, transparent 15%, transparent 85%, rgba(8,8,16,0.35) 100%)
        `,
      }} />
    </div>
  )
}
