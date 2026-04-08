import { CronExpression } from 'cron-expression';

interface CronExpressionDescriptor {
  minute: string;
  hour: string;
  dayOfMonth: string;
  month: string;
  dayOfWeek: string;
}

function parseCronExpression(expression: string): CronExpressionDescriptor {
  const parts = expression.split(' ');
  if (parts.length !== 5) {
    throw new Error('Invalid cron expression');
  }
  return {
    minute: parts[0],
    hour: parts[1],
    dayOfMonth: parts[2],
    month: parts[3],
    dayOfWeek: parts[4],
  };
}

function getNextRuns(expression: string, count: number): string[] {
  const descriptor = parseCronExpression(expression);
  const cron = new CronExpression(expression);
  const nextRuns: string[] = [];
  let date = new Date();
  while (nextRuns.length < count) {
    date = cron.next().toDate();
    nextRuns.push(date.toISOString());
  }
  return nextRuns;
}

function getHumanReadableDescription(expression: string): string {
  const descriptor = parseCronExpression(expression);
  // implement human-readable description logic here
  return 'Every day at 11:00 PM';
}

export function parseCron(expression: string) {
  try {
    const descriptor = parseCronExpression(expression);
    const nextRuns = getNextRuns(expression, 5);
    const description = getHumanReadableDescription(expression);
    return {
      valid: true,
      expression,
      description,
      nextRuns,
      schedule: descriptor,
      timezone: 'UTC',
    };
  } catch (error) {
    return {
      valid: false,
      expression,
      error: error.message,
    };
  }
}
