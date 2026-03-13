import { EventEmitter } from 'events';
import { logger } from './logger';

class SimpleQueue extends EventEmitter {
  constructor(private name: string) {
    super();
  }

  async add(jobName: string, data: any) {
    logger.info({ queue: this.name, jobName, data }, 'Job added to in-memory queue');
    // Process immediately or in next tick
    setImmediate(() => {
      this.emit('process', { id: Math.random().toString(36).substr(2, 9), name: jobName, data });
    });
  }
}

export const ticketQueue = new SimpleQueue('ticket-processing');

export const createWorker = (
  queueName: string,
  processor: (job: any) => Promise<any>
) => {
  // For in-memory, we just listen to the 'process' event
  ticketQueue.on('process', async (job) => {
    try {
      await processor(job);
      logger.info({ jobId: job.id, queue: queueName }, 'Job completed');
    } catch (err) {
      logger.error({ jobId: job.id, queue: queueName, err }, 'Job failed');
    }
  });

  return { on: (event: string, cb: Function) => {} }; // Mock worker returning
};
