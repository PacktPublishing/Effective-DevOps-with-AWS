const winston = require('winston');
const MockFireHoser = require('./support/mock-firehoser');
const WFireHose = require('../src/index.js');

describe('firehose logger transport', () => {
  const m = new MockFireHoser('test-stream', {});
  const message = 'test message';

  it('logs a message', done => {
    m.send(message)
      .then(response => {
        expect(response).toBe(message);
        done();
      })
      .catch(e => done(e));
  });

  it('affixes to winston', done => {
    const logger = new (winston.Logger)({
      transports: [
        new (WFireHose)({ firehoser: m }),
      ],
    });

    logger.info(message, (err, level, response) => {
      if (err) return done(err);
      expect(response).toBe(message);
      return done();
    });
  });
});
