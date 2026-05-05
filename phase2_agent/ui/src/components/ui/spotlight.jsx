import { useRef, useState, useCallback, useEffect } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'

export function Spotlight({ size = 320, springOptions = { bounce: 0 } }) {
  const containerRef = useRef(null)
  const [isHovered, setIsHovered] = useState(false)
  const [parentElement, setParentElement] = useState(null)

  const mouseX = useSpring(0, springOptions)
  const mouseY = useSpring(0, springOptions)
  const spotlightLeft = useTransform(mouseX, x => `${x - size / 2}px`)
  const spotlightTop  = useTransform(mouseY, y => `${y - size / 2}px`)

  useEffect(() => {
    if (containerRef.current) {
      const p = containerRef.current.parentElement
      if (p) { p.style.position = 'relative'; p.style.overflow = 'hidden'; setParentElement(p) }
    }
  }, [])

  const handleMouseMove = useCallback((e) => {
    if (!parentElement) return
    const { left, top } = parentElement.getBoundingClientRect()
    mouseX.set(e.clientX - left)
    mouseY.set(e.clientY - top)
  }, [mouseX, mouseY, parentElement])

  useEffect(() => {
    if (!parentElement) return
    const onEnter = () => setIsHovered(true)
    const onLeave = () => setIsHovered(false)
    parentElement.addEventListener('mousemove', handleMouseMove)
    parentElement.addEventListener('mouseenter', onEnter)
    parentElement.addEventListener('mouseleave', onLeave)
    return () => {
      parentElement.removeEventListener('mousemove', handleMouseMove)
      parentElement.removeEventListener('mouseenter', onEnter)
      parentElement.removeEventListener('mouseleave', onLeave)
    }
  }, [parentElement, handleMouseMove])

  return (
    <motion.div
      ref={containerRef}
      style={{
        pointerEvents: 'none',
        position: 'absolute',
        borderRadius: '50%',
        width: size,
        height: size,
        left: spotlightLeft,
        top: spotlightTop,
        background: 'radial-gradient(circle at center, rgba(16,163,127,0.18) 0%, rgba(16,163,127,0.06) 50%, transparent 80%)',
        filter: 'blur(32px)',
        opacity: isHovered ? 1 : 0,
        transition: 'opacity 0.2s ease',
      }}
    />
  )
}
