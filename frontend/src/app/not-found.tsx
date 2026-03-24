import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center bg-neutral-50">
      <h1 className="text-7xl font-bold text-neutral-900 tracking-tight">404</h1>
      <p className="mt-4 text-lg text-neutral-600 max-w-md">
        Страница не существует или была перемещена.
      </p>
      <Link href="/" className="btn-primary inline-flex mt-8">
        На главную
      </Link>
    </div>
  );
}