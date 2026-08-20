// frontend/app/page.tsx

// Fungsi untuk narik data dari FastAPI
// Karena berjalan di dalam jaringan Docker, Next.js bisa langsung memanggil nama service 'backend'
async function getProducts() {
  try {
    // cache: 'no-store' biar datanya selalu update (mirip getServerSideProps di Next.js lama)
    const res = await fetch('http://backend:8000/products/', { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch (error) {
    console.error("Gagal mengambil data produk:", error);
    return [];
  }
}

export default async function Home() {
  const products = await getProducts();

  return (
    <main className="min-h-screen bg-[#F9F9F9] text-gray-900 p-8 md:p-20">
      {/* Bagian Header Brand */}
      <header className="mb-20 pb-6 border-b border-gray-200">
        <h1 className="text-4xl tracking-[0.2em] font-light uppercase">Kala</h1>
        <p className="text-gray-500 mt-2 text-sm tracking-wide">The essence of space and living.</p>
      </header>

      {/* Bagian Grid Katalog Produk */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
        {products.length === 0 ? (
          <p className="text-gray-400 italic">Belum ada karya di etalase saat ini.</p>
        ) : (
          products.map((product: any) => (
            <div key={product.id} className="group cursor-pointer">
              {/* Kotak Placeholder Foto Produk */}
              <div className="w-full aspect-[3/4] bg-gray-200 mb-5 flex items-center justify-center transition-colors duration-300 group-hover:bg-gray-300">
                <span className="text-gray-400 text-xs tracking-widest">VISUAL</span>
              </div>
              
              {/* Info Produk */}
              <h2 className="text-lg font-medium tracking-wide">{product.name}</h2>
              <p className="text-gray-500 text-sm mt-2 mb-4 line-clamp-2 leading-relaxed">
                {product.description}
              </p>
              <p className="text-gray-900 font-medium">Rp {product.price}</p>
            </div>
          ))
        )}
      </section>
    </main>
  );
}