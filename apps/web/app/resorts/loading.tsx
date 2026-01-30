export default function ResortsLoading() {
  return (
    <main className="min-h-screen bg-white">
      {/* Breadcrumb skeleton */}
      <div className="bg-dark-50 py-4 border-b border-dark-100">
        <div className="container-page">
          <div className="h-5 w-32 bg-dark-100 rounded-lg animate-pulse" />
        </div>
      </div>

      {/* Hero skeleton */}
      <div className="py-20 sm:py-28">
        <div className="container-page space-y-6">
          <div className="h-4 w-48 bg-dark-100 rounded-lg animate-pulse" />
          <div className="h-12 w-96 max-w-full bg-dark-100 rounded-xl animate-pulse" />
          <div className="h-6 w-80 max-w-full bg-dark-100 rounded-lg animate-pulse" />
          <div className="h-14 w-96 max-w-full bg-dark-100 rounded-full animate-pulse mt-10" />
        </div>
      </div>

      {/* Filter bar skeleton */}
      <div className="border-b border-dark-100">
        <div className="container-page py-4">
          <div className="flex gap-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="h-9 w-20 bg-dark-100 rounded-full animate-pulse"
              />
            ))}
          </div>
        </div>
      </div>

      {/* Card grid skeleton */}
      <div className="container-page py-16">
        <div className="flex items-center gap-5 mb-10">
          <div className="w-14 h-14 bg-dark-100 rounded-2xl animate-pulse" />
          <div className="space-y-2">
            <div className="h-8 w-40 bg-dark-100 rounded-xl animate-pulse" />
            <div className="h-4 w-24 bg-dark-100 rounded-lg animate-pulse" />
          </div>
        </div>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-3xl border border-dark-100 overflow-hidden">
              <div className="aspect-[16/9] bg-dark-100 animate-pulse" />
              <div className="p-6 space-y-3">
                <div className="h-6 bg-dark-100 rounded-xl w-2/3 animate-pulse" />
                <div className="h-4 bg-dark-100 rounded-xl w-1/3 animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
