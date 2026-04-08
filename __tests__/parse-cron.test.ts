import { parseCron } from '../src/cron-parser';

describe('parseCron', () => {
  it('should parse a valid cron expression', () => {
    const expression = '0 23 * * *';
    const result = parseCron(expression);
    expect(result.valid).toBe(true);
    expect(result.expression).toBe(expression);
    expect(result.description).toBe('Every day at 11:00 PM');
    expect(result.nextRuns).toHaveLength(5);
    expect(result.schedule).toEqual({ minute: '0', hour: '23', dayOfMonth: '*', month: '*', dayOfWeek: '*' });
    expect(result.timezone).toBe('UTC');
  });

  it('should handle invalid cron expressions', () => {
    const expression = 'invalid';
    const result = parseCron(expression);
    expect(result.valid).toBe(false);
    expect(result.expression).toBe(expression);
    expect(result.error).not.toBeUndefined();
  });
});
