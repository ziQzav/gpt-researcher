from datetime import datetime
from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI
from .utils.views import print_agent_output

TEMPLATE = """You are an expert research article reviewer. \
Your goal is to review research drafts and provide feedback to the reviser only based on specific guidelines. \
"""

class ReviewerAgent:
    def __init__(self):
        pass

    def review_draft(self, draft_state: dict):
        """
        Review a draft article
        :param draft_state:
        :return:
        """
        task = draft_state.get("task")
        guidelines = '- '.join(guideline for guideline in task.get("guidelines"))
        revision_notes = draft_state.get("revision_notes")

        revise_prompt = f"""The reviser has already revised the draft based on your previous review notes with the following feedback:
{revision_notes}\n
Please provide additional feedback ONLY if critical since the reviser has already made changes based on your previous feedback.
If you think the article is sufficient or that non critical revisions are required, please aim to return None.
"""

        review_prompt = f"""You have been tasked with reviewing the draft which was written by a non-expert based on specific guidelines.
Please accept the draft if it is good enough to publish, or send it for revision, along with your notes to guide the revision.
If not all of the guideline criteria are met, you should send appropriate revision notes.
If the draft meets all the guidelines, please return None.
{revise_prompt if revision_notes else ""}

Guidelines: {guidelines}\nDraft: {draft_state.get("draft")}\n
"""
        prompt = [{
            "role": "system",
            "content": TEMPLATE
        }, {
            "role": "user",
            "content": review_prompt
        }]

        lc_messages = convert_openai_messages(prompt)
        response = ChatOpenAI(model='gpt-4-turbo', max_retries=1).invoke(lc_messages).content

        if 'None' in response:
            return None
        return response

    def run(self, draft_state: dict):
        task = draft_state.get("task")
        guidelines = task.get("guidelines")
        to_follow_guidelines = task.get("follow_guidelines")
        review = None
        if to_follow_guidelines:
            print_agent_output(f"Reviewing draft...", agent="REVIEWER")
            print_agent_output(f"Following guidelines {guidelines}...", agent="REVIEWER")
            review = self.review_draft(draft_state)
            print_agent_output(f"Review feedback {review}...", agent="REVIEWER")
        else:
            print_agent_output(f"Ignoring guidelines...", agent="REVIEWER")
        return {"review": review}
