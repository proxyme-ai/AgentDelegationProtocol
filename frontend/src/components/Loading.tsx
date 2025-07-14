interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  fullScreen?: boolean;
}

export function Loading({ size = 'md', text, fullScreen = false }: LoadingProps) {
  const getSizeClass = () => {
    switch (size) {
      case 'sm':
        return 'loading-sm';
      case 'lg':
        return 'loading-lg';
      default:
        return 'loading-md';
    }
  };

  const content = (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className={`loading loading-spinner ${getSizeClass()}`}></div>
      {text && (
        <p className="text-base-content/70 text-center">{text}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-base-100/80 backdrop-blur-sm flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
}

interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function Skeleton({ className = '', lines = 1 }: SkeletonProps) {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`bg-base-300 rounded ${
            i === lines - 1 ? 'h-4' : 'h-4 mb-2'
          } ${i === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full'}`}
        />
      ))}
    </div>
  );
}

interface LoadingCardProps {
  title?: string;
  lines?: number;
}

export function LoadingCard({ title, lines = 3 }: LoadingCardProps) {
  return (
    <div className="card bg-base-100 shadow">
      <div className="card-body">
        {title && (
          <div className="mb-4">
            <Skeleton className="h-6 w-1/2" />
          </div>
        )}
        <Skeleton lines={lines} />
      </div>
    </div>
  );
}

export default Loading;