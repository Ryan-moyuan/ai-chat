"""反馈系统 - 用户评价收集与统计"""
import core.memory_manager as memory


def give_feedback(message_id, is_good, comment=""):
    """
    提交反馈
    is_good: True = thumbs up, False = thumbs down
    """
    feedback_type = "thumbs_up" if is_good else "thumbs_down"
    memory.save_feedback(message_id, feedback_type, comment)


def get_stats():
    """获取反馈统计"""
    return memory.get_feedback_stats()
