import { createClient } from "@supabase/supabase-js";
import { Redis } from "@upstash/redis";
import pino from "pino";

const logger = pino({ level: process.env.LOG_LEVEL ?? "info" });

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const storageBucket = process.env.SUPABASE_STORAGE_BUCKET ?? "lyrics-audio";
const redisUrl = process.env.REDIS_URL;

if (!supabaseUrl || !supabaseKey || !redisUrl) {
  logger.error("Missing required env vars SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, REDIS_URL");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);
const redis = new Redis({ url: redisUrl });

type JobPayload = {
  jobId: string;
  userId: string;
  sourceUrl?: string;
  storagePath?: string;
  theme: "gradient" | "cover-blur" | "vhs";
  aiImages: boolean;
};

async function main() {
  logger.info("Worker started; listening for jobs");
  // Placeholder loop; replace with Redis blocking pop.
  setInterval(async () => {
    const job = await redis.lpop<JobPayload>("jobs:queue");
    if (!job) return;
    logger.info({ jobId: job.jobId }, "Picked job");
    try {
      await handleJob(job);
      logger.info({ jobId: job.jobId }, "Job completed");
    } catch (error) {
      logger.error({ jobId: job.jobId, error }, "Job failed");
      await updateStatus(job.jobId, "failed", String(error));
    }
  }, 1000);
}

async function handleJob(job: JobPayload) {
  await updateStatus(job.jobId, "processing");
  // TODO: download audio, hash, dedupe, run Whisper.cpp, generate SRT/JSON.
  // TODO: optional SDXL frames (cache by audio hash + section).
  // TODO: FFmpeg render 16:9 and 9:16 with selected theme, watermark toggle.
  // TODO: upload outputs to Supabase storage and record URLs.
  await updateStatus(job.jobId, "done");
}

async function updateStatus(jobId: string, status: string, error?: string) {
  const { error: dbError } = await supabase
    .from("jobs")
    .update({ status, error })
    .eq("id", jobId);
  if (dbError) {
    logger.error({ jobId, dbError }, "Failed to update job status");
  }
}

void main();
