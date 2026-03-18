import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return (
    <main className="flex min-h-[calc(100dvh-4rem)] flex-col items-center justify-center px-4">
      <h1 className="display-title rise-in mb-10 text-center text-6xl font-bold tracking-tight text-[var(--sea-ink)] sm:text-8xl lg:text-[10rem] lg:leading-[0.9]">
        Hello World
      </h1>
      <button
        type="button"
        onClick={() => alert(42)}
        className="rise-in cursor-pointer rounded-full border-2 border-[var(--lagoon)] bg-transparent px-10 py-4 text-lg font-bold tracking-wide text-[var(--lagoon)] uppercase transition-all duration-200 hover:-translate-y-1 hover:bg-[var(--lagoon)] hover:text-[var(--bg-base)] hover:shadow-[0_0_40px_rgba(79,184,178,0.4)] active:scale-95"
        style={{ animationDelay: "120ms" }}
      >
        The Answer
      </button>
    </main>
  );
}
