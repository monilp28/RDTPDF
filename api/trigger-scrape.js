// Serverless function to dispatch the GitHub Actions workflow that runs the scraper
// Configure these environment variables in Vercel:
// - GITHUB_TOKEN (repo scope)
// - ACTION_TRIGGER_SECRET (shared secret for simple auth)
// - GH_OWNER (optional, default: smitster1403)
// - GH_REPO (optional, default: red-deer-toyota)
// - GH_WORKFLOW_FILE (optional, default: .github/workflows/daily-scrape.yml)

module.exports = async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const provided = req.headers['x-action-secret'] || req.headers['x-action-secret'.toLowerCase()];
    const expected = process.env.ACTION_TRIGGER_SECRET;
    // If a secret is configured, require it; otherwise allow open (use with caution)
    if (expected && provided !== expected) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const token = process.env.GITHUB_TOKEN;
    if (!token) {
      return res.status(500).json({ error: 'Missing GITHUB_TOKEN env' });
    }

    const owner = process.env.GH_OWNER || 'smitster1403';
    const repo = process.env.GH_REPO || 'red-deer-toyota';
    const workflow = process.env.GH_WORKFLOW_FILE || '.github/workflows/daily-scrape.yml';
    const ref = req.query.ref || 'master';

    const url = `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${encodeURIComponent(workflow)}/dispatches`;

    const ghRes = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json',
        'User-Agent': `${owner}-${repo}-trigger`
      },
      body: JSON.stringify({ ref })
    });

    if (!ghRes.ok) {
      const txt = await ghRes.text();
      return res.status(ghRes.status).json({ error: 'GitHub dispatch failed', details: txt });
    }

    return res.status(202).json({ ok: true, message: 'Scrape workflow dispatched', ref });
  } catch (e) {
    return res.status(500).json({ error: e?.message || 'Internal Error' });
  }
}
