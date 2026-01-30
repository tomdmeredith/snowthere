export default function ResortDetailLoading() {
  return (
    <main className="min-h-screen bg-white">
      {/* Breadcrumb skeleton */}
      <div className="bg-dark-50 py-4 border-b border-dark-100">
        <div className="container-page">
          <div className="h-5 w-64 bg-dark-100 rounded-lg animate-pulse" />
        </div>
      </div>

      {/* Hero skeleton */}
      <div className="relative">
        <div className="aspect-[21/9] max-h-[480px] bg-dark-100 animate-pulse" />
      </div>

      {/* Content skeleton */}
      <div className="container-page py-12">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Title */}
          <div className="space-y-4">
            <div className="h-10 w-72 bg-dark-100 rounded-xl animate-pulse" />
            <div className="h-5 w-48 bg-dark-100 rounded-lg animate-pulse" />
          </div>

          {/* Quick Take card */}
          <div className="rounded-3xl border border-dark-100 p-8 space-y-4">
            <div className="h-6 w-32 bg-dark-100 rounded-xl animate-pulse" />
            <div className="h-4 w-full bg-dark-100 rounded-lg animate-pulse" />
            <div className="h-4 w-5/6 bg-dark-100 rounded-lg animate-pulse" />
            <div className="h-4 w-4/6 bg-dark-100 rounded-lg animate-pulse" />
          </div>

          {/* Metrics table */}
          <div className="rounded-3xl border border-dark-100 overflow-hidden">
            <div className="h-12 bg-dark-50 animate-pulse" />
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="h-12 border-t border-dark-100 animate-pulse"
                style={{ animationDelay: `${i * 100}ms` }}
              />
            ))}
          </div>

          {/* Content sections */}
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-4">
              <div className="h-7 w-48 bg-dark-100 rounded-xl animate-pulse" />
              <div className="h-4 w-full bg-dark-100 rounded-lg animate-pulse" />
              <div className="h-4 w-5/6 bg-dark-100 rounded-lg animate-pulse" />
              <div className="h-4 w-3/4 bg-dark-100 rounded-lg animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
