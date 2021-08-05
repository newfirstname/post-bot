const db = require('../db/db');

exports.addSource = async (sourceId, conId) => {
  const consWithThisIdInDests = await db.exec(
    'SELECT id FROM connectors WHERE $1 = ANY (destinations)',
    [sourceId.toLowerCase()]
  );

  // check if id is not in destinations
  if (consWithThisIdInDests.length === 0) {
    // check if source is in this connector
    const hasSource = await db.exec(
      'SELECT id FROM connectors WHERE $1 = ANY (sources) AND id = $2',
      [sourceId.toLowerCase(), conId]
    );

    if (hasSource.length === 0) {
      await db.exec(
        'UPDATE connectors SET sources = array_cat(sources, $1) WHERE id = $2',
        [[sourceId.toLowerCase()], conId]
      );

      return 'success';
    } else {
      return 'hassource';
    }
  } else {
    // the id was found in destinations therefor it can't be in sources
    return 'isindests';
  }
};

exports.addDest = async (destId, conId) => {
  const consWithThisIdInSource = await db.exec(
    'SELECT id FROM connectors WHERE $1 = ANY (sources)',
    [destId.toLowerCase()]
  );

  // check if id is not in sources
  if (consWithThisIdInSource.length === 0) {
    // check if dest is in this connector
    const hasDest = await db.exec(
      'SELECT id FROM connectors WHERE $1 = ANY (destinations) AND id = $2',
      [destId.toLowerCase(), conId]
    );

    if (hasDest.length === 0) {
      await db.exec(
        'UPDATE connectors SET destinations = array_cat(destinations, $1) WHERE id = $2',
        [[destId.toLowerCase()], conId]
      );

      return 'success';
    } else {
      return 'hasdest';
    }
  } else {
    // the id was found in sources therefor it can't be in dests
    return 'isinsources';
  }
};

exports.removeSource = async (sourceId, conId) => {
  await db.exec(
    'UPDATE connectors SET sources = array_remove(sources, $1) WHERE id = $2',
    [sourceId.toLowerCase(), conId]
  );
};

exports.removeDest = async (destId, conId) => {
  await db.exec(
    'UPDATE connectors SET destinations = array_remove(destinations, $1) WHERE id = $2',
    [destId.toLowerCase(), conId]
  );
};

exports.saveRules = async (rules, conId) => {
  await db.exec('UPDATE connectors SET rules = $1 WHERE id = $2', [
    rules,
    conId,
  ]);
};
