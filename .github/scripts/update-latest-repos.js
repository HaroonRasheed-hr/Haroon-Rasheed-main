// Fetches newest public repos and rewrites the README section between:
// <!--START_SECTION:repos--> and <!--END_SECTION:repos-->

const fs = require("fs");

const USERNAME = process.env.GH_USERNAME || "Zubair-hussain";
const TOKEN = process.env.GH_TOKEN;
const README_PATH = "README.md";
const START_MARKER = "<!--START_SECTION:repos-->";
const END_MARKER = "<!--END_SECTION:repos-->";
const MAX_REPOS = 5;

function escapeMarkdown(text) {
  return String(text).replace(/\|/g, "\\|").replace(/\r?\n/g, " ").trim();
}

async function main() {
  const headers = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
  };

  if (TOKEN) {
    headers.Authorization = `Bearer ${TOKEN}`;
  }

  const res = await fetch(
    `https://api.github.com/users/${USERNAME}/repos?sort=created&direction=desc&per_page=30`,
    { headers }
  );

  if (!res.ok) {
    throw new Error(`GitHub API error: ${res.status} ${res.statusText}`);
  }

  const repos = await res.json();
  const latest = repos
    .filter((repo) => !repo.fork && !repo.archived)
    .slice(0, MAX_REPOS);

  const lines = latest.map((repo) => {
    const description = repo.description
      ? escapeMarkdown(repo.description)
      : "No description yet";
    const language = repo.language ? ` \`${escapeMarkdown(repo.language)}\`` : "";
    const stars = repo.stargazers_count > 0 ? ` Stars: ${repo.stargazers_count}` : "";

    return `- [${repo.name}](${repo.html_url}) - ${description}${language}${stars}`;
  });

  const fallback = "- Latest repositories will appear here after the workflow runs.";
  const block = `${START_MARKER}\n${lines.length ? lines.join("\n") : fallback}\n${END_MARKER}`;

  const readme = fs.readFileSync(README_PATH, "utf8");
  const regex = new RegExp(`${START_MARKER}[\\s\\S]*?${END_MARKER}`);

  if (!regex.test(readme)) {
    throw new Error(
      "Markers not found in README.md. Add <!--START_SECTION:repos--> and <!--END_SECTION:repos-->."
    );
  }

  fs.writeFileSync(README_PATH, readme.replace(regex, block));
  console.log(`Updated README with ${latest.length} latest repos.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
