"use client";

import { useEffect, useState } from "react";
import { useProjectStore } from "@/hooks/use-project-store";
import { Button } from "@/components/ui/button";
import { seedProject } from "@/data/seedProject";
import { type Project } from "@/types/project";
import { Download, PlayCircle, RefreshCcw } from "lucide-react";

const STORAGE_KEY = "lyricforge-projects";

export default function ProjectsPage() {
  const { loadProject } = useProjectStore();
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        setProjects(JSON.parse(raw));
      } catch (err) {
        console.error(err);
      }
    }
  }, []);

  const loadDemo = () => {
    loadProject(seedProject);
  };

  return (
    <div className="space-y-4">
      <div className="glass-panel p-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Projects</h2>
          <p className="text-sm text-white/60">Stored locally in your browser</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadDemo} className="flex items-center gap-2">
            <PlayCircle className="h-4 w-4" /> Load demo
          </Button>
          <Button variant="ghost" onClick={() => window.location.reload()} className="flex items-center gap-2">
            <RefreshCcw className="h-4 w-4" /> Refresh
          </Button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
        {projects.map((project) => (
          <div key={project.id} className="glass-panel p-4 space-y-2 border border-white/10">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">{project.name}</p>
                <p className="text-xs text-white/60">Updated {new Date(project.updatedAt).toLocaleString()}</p>
              </div>
              <Button variant="outline" onClick={() => loadProject(project)} className="text-xs">Open</Button>
            </div>
            <p className="text-sm text-white/70">{project.lyrics.length} lines · {project.audio?.fileName ?? "No audio"}</p>
          </div>
        ))}

        {!projects.length && (
          <div className="glass-panel p-6 border border-white/10">
            <p className="font-semibold mb-2">No saved projects yet</p>
            <p className="text-sm text-white/70 mb-3">Use the Studio to create one, then hit Save. Or load the demo song.</p>
            <Button onClick={loadDemo} className="flex items-center gap-2">
              <Download className="h-4 w-4" /> Load demo project
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
