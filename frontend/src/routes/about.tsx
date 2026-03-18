import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/about")({ component: About });

function About() {
  return (
    <main className="flex min-h-[calc(100dvh-4rem)] flex-col items-center justify-center px-4">
      <div className="rise-in max-w-xl text-center">
        <h1 className="display-title mb-4 text-4xl font-bold text-[var(--sea-ink)] sm:text-5xl">
          About
        </h1>
        <p className="text-lg leading-relaxed text-[var(--sea-ink-soft)]">
          A minimal starting point. Nothing more, nothing less.
        </p>
      </div>
    </main>
  );
}
