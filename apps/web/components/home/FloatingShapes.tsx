'use client'

import { useEffect, useState } from 'react'

interface ShapeConfig {
  id: string
  type: 'circle' | 'triangle' | 'square' | 'diamond'
  color: string
  size: number
  position: { top?: string; bottom?: string; left?: string; right?: string }
  parallaxSpeed: number
  animationDelay: string
}

const SHAPES: ShapeConfig[] = [
  {
    id: 'circle-1',
    type: 'circle',
    color: 'rgba(255, 107, 107, 0.15)', // coral
    size: 128,
    position: { top: '10%', left: '5%' },
    parallaxSpeed: 0.02,
    animationDelay: '0s',
  },
  {
    id: 'triangle-1',
    type: 'triangle',
    color: 'rgba(78, 205, 196, 0.15)', // teal
    size: 80,
    position: { top: '15%', right: '10%' },
    parallaxSpeed: -0.03,
    animationDelay: '1s',
  },
  {
    id: 'square-1',
    type: 'square',
    color: 'rgba(255, 224, 102, 0.15)', // gold
    size: 96,
    position: { bottom: '20%', left: '15%' },
    parallaxSpeed: 0.015,
    animationDelay: '2s',
  },
  {
    id: 'diamond-1',
    type: 'diamond',
    color: 'rgba(149, 225, 211, 0.15)', // mint
    size: 80,
    position: { bottom: '30%', right: '8%' },
    parallaxSpeed: -0.025,
    animationDelay: '1.5s',
  },
  {
    id: 'circle-2',
    type: 'circle',
    color: 'rgba(78, 205, 196, 0.1)', // teal
    size: 64,
    position: { top: '40%', left: '3%' },
    parallaxSpeed: 0.01,
    animationDelay: '0.5s',
  },
  {
    id: 'square-2',
    type: 'square',
    color: 'rgba(255, 107, 107, 0.1)', // coral
    size: 48,
    position: { top: '25%', right: '25%' },
    parallaxSpeed: -0.02,
    animationDelay: '2.5s',
  },
]

function Shape({ config, mousePosition }: { config: ShapeConfig; mousePosition: { x: number; y: number } }) {
  const translateX = mousePosition.x * config.parallaxSpeed
  const translateY = mousePosition.y * config.parallaxSpeed

  const baseStyle = {
    position: 'absolute' as const,
    ...config.position,
    transform: `translate(${translateX}px, ${translateY}px)`,
    transition: 'transform 0.3s ease-out',
    animation: `float 6s ease-in-out infinite`,
    animationDelay: config.animationDelay,
  }

  switch (config.type) {
    case 'circle':
      return (
        <div
          style={{
            ...baseStyle,
            width: config.size,
            height: config.size,
            borderRadius: '50%',
            backgroundColor: config.color,
          }}
        />
      )
    case 'triangle':
      return (
        <div
          style={{
            ...baseStyle,
            width: 0,
            height: 0,
            borderLeft: `${config.size / 2}px solid transparent`,
            borderRight: `${config.size / 2}px solid transparent`,
            borderBottom: `${config.size * 0.866}px solid ${config.color}`,
            backgroundColor: 'transparent',
          }}
        />
      )
    case 'square':
      return (
        <div
          style={{
            ...baseStyle,
            width: config.size,
            height: config.size,
            backgroundColor: config.color,
            transform: `rotate(12deg) translate(${translateX}px, ${translateY}px)`,
          }}
        />
      )
    case 'diamond':
      return (
        <div
          style={{
            ...baseStyle,
            width: config.size,
            height: config.size,
            backgroundColor: config.color,
            transform: `rotate(45deg) translate(${translateX}px, ${translateY}px)`,
          }}
        />
      )
    default:
      return null
  }
}

export function FloatingShapes() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // Normalize mouse position relative to viewport center
      const x = (e.clientX - window.innerWidth / 2) / window.innerWidth
      const y = (e.clientY - window.innerHeight / 2) / window.innerHeight
      setMousePosition({ x: x * 100, y: y * 100 })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {SHAPES.map((shape) => (
        <Shape key={shape.id} config={shape} mousePosition={mousePosition} />
      ))}
    </div>
  )
}
