import { Injectable } from '@nestjs/common';
import { nanoid } from 'nanoid';
import { Project } from '@lyricforge/shared';

@Injectable()
export class ExportsService {
  queueExport(project: Project) {
    const jobId = `job_${nanoid(8)}`;
    return {
      jobId,
      status: 'queued' as const,
      preset: project.export.preset,
      projectId: project.id,
      estimatedSeconds: 15
    };
  }
}
