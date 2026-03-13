import { Queue, Worker, Job } from 'bullmq';
import { config } from './config';
import { logger } from './logger';

export const connection = {
  url: config.REDIS_URL,
};

export const ticketQueue = new Queue('ticket-processing', { connection });

logger.info(`BullMQ connected to Redis at ${config.REDIS_URL}`);

export const createWorker = (
  queueName: string,
  processor: (job: Job) => Promise<any>
) => {
  const worker = new Worker(queueName, processor, { connection });
  
  worker.on('completed', (job: Job) => {
    logger.info({ jobId: job.id, queue: queueName }, 'Job completed');
  });

  worker.on('failed', (job: Job | undefined, err: Error) => {
    logger.error({ jobId: job?.id, queue: queueName, err }, 'Job failed');
  });

  return worker;
};
