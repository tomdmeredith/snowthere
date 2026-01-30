export default function GuideDetailLoading() {
  return (
    <main className="min-h-screen bg-white">
      {/* Breadcrumb skeleton */}
      <div className="bg-dark-50 py-4 border-b border-dark-100">
        <div className="container-page">
          <div className="h-5 w-48 bg-dark-100 rounded-lg animate-pulse" />
        </div>
      </div>

      {/* Hero skeleton */}
      <div className="py-16 bg-gradient-to-br from-teal-50 to-white">
        <div className="container-page space-y-4">
          <div className="h-4 w-32 bg-dark-100 rounded-lg animate-pulse" />
          <div className="h-12 w-96 max-w-full bg-dark-100 rounded-xl animate-pulse" />
          <div className="h-5 w-80 max-w-full bg-dark-100 rounded-lg animate-pulse" />
        </div>
      </div>

      {/* Content skeleton */}
      <div className="container-page py-12">
        <div className="max-w-3xl mx-auto space-y-8">
          {/* Hero image */}
          <div className="aspect-[16/9] bg-dark-100 rounded-3xl animate-pulse" />

          {/* Paragraphs */}
          {[1, 2, 3, 4].map((section) => (
            <div key={section} className="space-y-4">
              <div className="h-7 w-56 bg-dark-100 rounded-xl animate-pulse" />
              <div className="h-4 w-full bg-dark-100 rounded-lg animate-pulse" />
              <div className="h-4 w-5/6 bg-dark-100 rounded-lg animate-pulse" />
              <div className="h-4 w-4/6 bg-dark-100 rounded-lg animate-pulse" />
              <div className="h-4 w-full bg-dark-100 rounded-lg animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
