import { useEffect, useMemo, useState } from "react";
import { Check, ImageIcon, Sparkles } from "lucide-react";

type Props = {
  prompt?: string;
};

export function ImageGenerationLoader({ prompt }: Props) {
  const [progress, setProgress] = useState(8);
  const steps = useMemo(
    () => [
      {
        threshold: 12,
        title: "Understanding prompt",
        detail: "Checking tone and reverence",
      },
      {
        threshold: 32,
        title: "Creating composition",
        detail: "Building scene structure",
      },
      {
        threshold: 58,
        title: "Rendering image",
        detail: "Generating light, texture, and detail",
      },
      {
        threshold: 86,
        title: "Final enhancement",
        detail: "Preparing the finished artwork",
      },
    ],
    [],
  );

  useEffect(() => {
    const interval = window.setInterval(() => {
      setProgress((current) => {
        if (current >= 94) return current;
        const increment = current < 35 ? 4 : current < 70 ? 2 : 1;
        return Math.min(94, current + increment);
      });
    }, 900);

    return () => window.clearInterval(interval);
  }, []);

  return (
    <div className="relative overflow-hidden rounded-lg border border-[#e5e7eb] bg-white p-4 text-[#111111]">
      <div className="grid gap-5 lg:grid-cols-[1fr_220px] lg:items-center">
        <div>
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-[#f5f5f5] px-3 py-1.5 text-xs font-medium text-[#374151]">
            <span className="image-pulse-dot h-2 w-2 rounded-full bg-[#111111]" />
            Image generation in progress
          </div>

          <h3 className="display-title mb-2 text-xl">
            Creating your image<span className="text-[#3b82f6]">.</span>
          </h3>

          <p className="mb-4 text-sm leading-6 text-[#6b7280]">
            ScriptureGuard is refining the prompt, composing the scene, and rendering a
            reverent Christian image.
          </p>

          <div className="image-shimmer mb-5 rounded-md border border-[#e5e7eb] bg-[#f8f9fa] p-3">
            <div className="mb-1 text-xs font-medium text-[#898989]">Prompt</div>
            <div className="text-sm font-medium leading-6 text-[#111111]">
              {prompt || "Reverent Christian artwork"}
            </div>
          </div>

          <div className="grid gap-3">
            {steps.map((step, index) => (
              <LoaderStep
                key={step.title}
                complete={progress >= step.threshold}
                active={
                  progress < step.threshold &&
                  (index === 0 || progress >= steps[index - 1].threshold)
                }
                title={step.title}
                detail={step.detail}
              />
            ))}
          </div>
        </div>

        <div className="mx-auto w-full max-w-[220px]">
          <div className="relative">
            <div className="image-shimmer relative aspect-[4/5] overflow-hidden rounded-xl border border-[#e5e7eb] bg-[#f5f5f5] shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
              <div className="absolute inset-0 grid grid-rows-[44px_1fr_72px]">
                <div className="flex items-center gap-2 border-b border-[#e5e7eb] bg-white px-4">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#ef4444]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[#f59e0b]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[#10b981]" />
                </div>
                <div className="relative bg-[#f8f9fa]">
                  <div className="absolute left-5 right-5 top-6 h-20 rounded-lg bg-white" />
                  <div className="absolute left-5 right-10 top-32 h-3 rounded-full bg-[#e5e7eb]" />
                  <div className="absolute left-5 right-16 top-40 h-3 rounded-full bg-[#e5e7eb]" />
                  <div className="absolute bottom-8 left-5 right-5 grid grid-cols-3 gap-2">
                    <span className="h-12 rounded-md bg-white" />
                    <span className="h-12 rounded-md bg-white" />
                    <span className="h-12 rounded-md bg-white" />
                  </div>
                </div>
                <div className="border-t border-[#e5e7eb] bg-white p-4" />
              </div>
              <div className="absolute inset-0 grid place-items-center">
                <div className="relative grid h-20 w-20 place-items-center rounded-full border-4 border-[#e5e7eb] bg-white">
                  <Sparkles aria-hidden="true" className="text-[#111111]" size={25} />
                  <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-[#111111] animate-spin" />
                </div>
              </div>
              <div className="absolute inset-x-0 bottom-0 p-4">
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 font-medium text-[#111111]">
                    <ImageIcon aria-hidden="true" size={15} />
                    Rendering
                  </span>
                  <span className="font-semibold text-[#111111]">{progress}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-[#e5e7eb]">
                  <div
                    className="h-full rounded-full bg-[#111111] transition-[width] duration-700 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LoaderStep({
  complete,
  active,
  title,
  detail,
}: {
  complete?: boolean;
  active?: boolean;
  title: string;
  detail: string;
}) {
  return (
    <div className="image-step flex items-center gap-3">
      <div
        className={`grid h-8 w-8 shrink-0 place-items-center rounded-full ${
          complete
            ? "bg-[#111111] text-white"
            : active
              ? "bg-[#111111] text-white"
              : "border border-[#e5e7eb] text-[#898989]"
        }`}
      >
        {complete ? (
          <Check aria-hidden="true" size={15} />
        ) : active ? (
          <span className="h-2.5 w-2.5 rounded-full bg-white animate-ping" />
        ) : (
          <span className="h-1.5 w-1.5 rounded-full bg-[#898989]" />
        )}
      </div>
      <div>
        <div className={`text-sm font-medium ${complete || active ? "text-[#111111]" : "text-[#898989]"}`}>
          {title}
        </div>
        <div className="text-xs text-[#6b7280]">{detail}</div>
      </div>
    </div>
  );
}
