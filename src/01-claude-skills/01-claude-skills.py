import os

from anthropic import Anthropic
from anthropic.lib import files_from_dir

from dotenv import load_dotenv

load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError(
        "ANTHROPIC_API_KEY not found. "
        "Copy ../.env.example to ../.env and add your API key."
    )

# =================================
# Initialize client
# =================================

client = Anthropic()

# =================================
# 1. Create skill
# =================================

skill = client.beta.skills.create(
    display_title="veo3",
    files=files_from_dir("skills/veo3-image-prompt")
)

# =================================
# 2. List skills
# =================================

def list_skills(client):
    skills = client.beta.skills.list(
        betas=["skills-2025-10-02"]
    )

    for skill in skills.data:
        print(f"{skill.id}: {skill.display_title}")

list_skills(client)

# =================================
# 3. Use a skill
# =================================
def test_skill(
    client: Anthropic,
    skill_id: str,
    prompt: str,
    model: str = "claude-sonnet-4-5-20250929",
):
    """
    Test a custom skill with a prompt.

    Args:
        client: Anthropic client
        skill_id: ID of skill to test
        prompt: Prompt to test the skill
        model: Model to use for testing

    Returns:
        Response from Claude
    """
    response = client.beta.messages.create(
        model=model,
        max_tokens=4096,
        container={
            "skills": [{"type": "custom", "skill_id": skill_id, "version": "latest"}]
        },
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
        messages=[{"role": "user", "content": prompt}],
        betas=[
            "code-execution-2025-08-25",
            "files-api-2025-04-14",
            "skills-2025-10-02",
        ],
    )

    return response


# =================================
# 4. Delete a skill
# =================================

def delete_skill(client: Anthropic, skill_id: str):

    versions = client.beta.skills.versions.list(skill_id=skill_id)

    for version in versions.data:
        client.beta.skills.versions.delete(
            skill_id=skill_id, version=version.version
        )

    # Then delete the skill itself
    client.beta.skills.delete(skill_id)

    return True

# =================================
# 5. Complete example
# =================================

SKILL_ID = "skill_01AuxL3XAUNm6jMfmY4CFHmm"

PROMPT = """
Improve this prompt for veo3:

Woman walks through a park.

Return only the improved prompt with no other commentary
"""

response = test_skill(client, SKILL_ID, PROMPT)

for msg in response.content:
    if msg.type == "text":
        print(msg.text)
