import { CronExpression } from 'cron-expression';

export function parseCron(expression: string) {
  try {
    const cron = new CronExpression(expression);
    const nextRuns: string[] = [];
    const now = new Date();
    for (let i = 0; i < 5; i++) {
      const next = cron.next().toDate();
      nextRuns.push(next.toISOString());
    }
    return {
      valid: true,
      expression,
      description: getDescription(expression),
      nextRuns,
      schedule: getSchedule(expression),
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

function getDescription(expression: string) {
  // Implement human-readable description generation
  // based on the cron expression
  const parts = expression.split(' ');
  if (parts.length !== 5) {
    return 'Invalid cron expression';
  }
  const [minute, hour, dayOfMonth, month, dayOfWeek] = parts;
  if (minute === '*' && hour === '*' && dayOfMonth === '*' && month === '*' && dayOfWeek === '*') {
    return 'Every minute';
  } else if (minute === '0' && hour === '*' && dayOfMonth === '*' && month === '*' && dayOfWeek === '*') {
    return 'Every hour';
  } else if (minute === '0' && hour === '9' && dayOfMonth === '*' && month === '*' && dayOfWeek === '*') {
    return 'Every day at 9:00 AM';
  } else if (minute === '0' && hour === '9' && dayOfMonth === '*' && month === '*' && dayOfWeek === '1') {
    return 'Every Monday at 9:00 AM';
  } else if (minute === '0' && hour === '9' && dayOfMonth === '1' && month === '*' && dayOfWeek === '*') {
    return 'At 9:00 AM on the 1st of every month';
  } else {
    return 'Custom cron expression';
  }
}

function getSchedule(expression: string) {
  const parts = expression.split(' ');
  if (parts.length !== 5) {
    return {};
  }
  const [minute, hour, dayOfMonth, month, dayOfWeek] = parts;
  return {
    minute,
    hour,
    dayOfMonth,
    month,
    dayOfWeek,
  };
  }
