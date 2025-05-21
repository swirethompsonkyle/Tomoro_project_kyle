from __future__ import annotations

import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from convfinqa.agents.judge_agent import JudgeAgent
from convfinqa.agents.solver_agent import SolverAgent
from convfinqa.dataset import FinQADataset
from convfinqa.utils import configure_logging


class ConvFinQAAgent:
    """High-level runner that coordinates Solver → Judge → metrics."""

    def __init__(
        self,
        *,
        data_file: str | os.PathLike = "data/dev.json",
        sample_size: int = 100,
        out_file: str | os.PathLike = "convfinqa_results.csv",
    ) -> None:
        load_dotenv()

        self.dataset = FinQADataset(data_file)
        self.sample_size = sample_size
        self.out_path = Path(out_file)
        self.logger = configure_logging()

        self.solver = SolverAgent()
        self.judge = JudgeAgent()


    def run(self) -> None:
        """Run the  loop and persist results to *self.out_path* with the full run's metrics."""
        sample = self.dataset.sample(self.sample_size)
        result_fields = ["id", "turn", "question", "ai_answer", "expected", "verdict"]

        turn_durations: list[float] = []
        conv_durations: list[float] = []
        conv_turn_counts: list[int] = []
        conv_correct_counts: list[int] = []

        total = correct = 0
        tic = time.time()

        with self.out_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=result_fields)
            writer.writeheader()

            for entry in sample:
                context = FinQADataset.build_context(entry)
                history: str = ""

                dialogue = (
                        entry.get("annotation", {}).get("dialogue_break")
                        or [entry["qa"]["question"]]
                )
                gold_list = (
                        entry.get("annotation", {}).get("exe_ans_list")
                        or [entry["qa"]["exe_ans"]]
                )

                conv_start = time.time()
                conv_correct = 0

                for turn, (question, gold) in enumerate(zip(dialogue, gold_list)):
                    turn_start = time.time()
                    ai_ans = self.solver.solve(context, question, history)

                    verdict, _prompt = self.judge.judge(
                        context=context + "\n\n" + history,
                        question=question,
                        expected=str(gold),
                        ai_answer=ai_ans,
                        qa_data=entry.get("qa"),
                    )

                    turn_durations.append(time.time() - turn_start)


                    total += 1
                    if not verdict.lower().startswith("incorrect"):
                        correct += 1
                        conv_correct += 1

                    writer.writerow(
                        dict(
                            id=entry["id"],
                            turn=turn,
                            question=question,
                            ai_answer=ai_ans,
                            expected=gold,
                            verdict=verdict,
                        )
                    )

                    history += f"[Q: {question} | A: {ai_ans}]\n"

                    self.logger.info(f"► Q{turn}: {question}")
                    self.logger.info(f"AI  : {ai_ans}")
                    self.logger.info(f"gold: {gold}")
                    self.logger.info(f"JDG : {verdict}\n")

                conv_durations.append(time.time() - conv_start)
                conv_turn_counts.append(turn + 1)
                conv_correct_counts.append(conv_correct)


        elapsed = time.time() - tic
        accuracy = 100.0 * correct / total if total else 0.0

        import statistics as stats

        conv_acc = [c / t for c, t in zip(conv_correct_counts, conv_turn_counts)]

        metrics = {
            "total_elapsed_s": elapsed,
            "avg_time_per_conversation_s": stats.mean(conv_durations),
            "avg_time_per_turn_s": stats.mean(turn_durations),

            "p95_time_per_turn_s": stats.quantiles(turn_durations, n=20)[18],  # 95-th %

            "turn_throughput_per_s": total / elapsed if elapsed else 0.0,

            "total_conversations": len(conv_durations),
            "avg_turns_per_conversation": stats.mean(conv_turn_counts),

            "conversation_accuracy_mean_pct": 100 * stats.mean(conv_acc),
            "conversation_accuracy_stddev_pct": 100 * stats.stdev(conv_acc) if len(conv_acc) > 1 else 0.0,
            "pct_conversations_fully_correct": 100 * sum(a == 1.0 for a in conv_acc) / len(conv_acc),
        }

        self.logger.info(f"Finished {total} turns in {elapsed:.1f}s — accuracy {accuracy:.2f}%")
        for k, v in metrics.items():
            self.logger.info(f"{k}: {v:.3f}")
