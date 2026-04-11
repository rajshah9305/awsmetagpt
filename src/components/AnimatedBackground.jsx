// Lightweight wrapper — no animated blobs, clean enterprise background
const AnimatedBackground = ({ children, className = '' }) => (
  <div className={`relative min-h-screen bg-surface ${className}`}>
    <div className="relative z-10">{children}</div>
  </div>
)

export default AnimatedBackground
