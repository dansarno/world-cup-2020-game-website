from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from . import models


@receiver(post_save, sender=models.GroupMatch)
def match_result(sender, instance, **kwargs):
    pass
    # correct_outcome = None
    # if instance.result:
    #     correct_outcome = instance.groupmatchoutcome_set.get(choice=instance.result)
    # for event in models.CalledBet.objects.all():
    #     if instance == event.get_outcome().match:
    #         if correct_outcome:
    #             event.outcome.group_match_outcome = correct_outcome
    #             event.outcome.save()
    #             event.save()
    #         else:
    #             event.outcome.delete()
    #             event.delete()
    #         return
    # new_outcome = models.Outcome.objects.create(group_match_outcome=correct_outcome)
    # models.CalledBet.objects.create(outcome=new_outcome)
    # return


def recalculate_scores_and_positions_delete(instance):
    called_bets_after_this_one = models.CalledBet.objects.filter(date__gt=instance.date).order_by('date')
    previous_called_bet_to_this_one = models.CalledBet.objects.filter(date__lt=instance.date).last()
    entries = models.Entry.objects.all()
    if previous_called_bet_to_this_one:
        # Restore scores back to the value before the called bet instance
        for entry in entries:
            entry.current_score = models.ScoreLog.objects. \
                filter(entry=entry, called_bet=previous_called_bet_to_this_one).first().score
            entry.save()
    else:
        # Restore scores back to zero
        entries.update(current_score=0)
    for called_bet in called_bets_after_this_one:
        # 1. Update scores for those that won this called bet
        for entry in entries:
            bet_in_same_group = models.Bet.objects.filter(entry=entry,
                                                          outcome__choice_group=called_bet.outcome.choice_group
                                                          ).first()
            if bet_in_same_group.outcome == called_bet.outcome:
                entry.current_score += called_bet.outcome.winning_amount
                entry.save()
                bet_in_same_group.success = True
            else:
                bet_in_same_group.success = False
            bet_in_same_group.called_bet = called_bet
            bet_in_same_group.save()

            score_log = models.ScoreLog.objects.filter(entry=entry, called_bet=called_bet).first()
            score_log.score = entry.current_score
            score_log.save()

        # 2. Update positions given the new scores
        position = 1
        ordered_entries = models.Entry.objects.order_by('-current_score', 'profile__user__first_name')
        previous_score = ordered_entries[0].current_score
        for i, entry in enumerate(ordered_entries):
            if entry.current_score < previous_score:
                position = i + 1
            entry.current_position = position
            entry.save()

            position_log = models.PositionLog.objects.filter(entry=entry, called_bet=called_bet).first()
            position_log.position = position
            position_log.save()

            previous_score = entry.current_score


def recalculate_from_instance(instance, created):
    called_bets_including_and_after_this_one = models.CalledBet.objects.filter(date__gte=instance.date).order_by('date')
    previous_called_bet_to_this_one = models.CalledBet.objects.filter(date__lt=instance.date).last()
    entries = models.Entry.objects.all()
    if previous_called_bet_to_this_one:
        # Restore scores back to the value before the called bet instance
        for entry in entries:
            entry.current_score = models.ScoreLog.objects.\
                filter(entry=entry, called_bet=previous_called_bet_to_this_one).first().score
            entry.save()
    else:
        # Restore scores back to zero
        entries.update(current_score=0)
    for called_bet in called_bets_including_and_after_this_one:
        # 1. Update scores for those that won this called bet
        for entry in entries:
            bet_in_same_group = models.Bet.objects.filter(entry=entry,
                                                          outcome__choice_group=called_bet.outcome.choice_group
                                                          ).first()
            if bet_in_same_group.outcome == called_bet.outcome:
                entry.current_score += called_bet.outcome.winning_amount
                entry.save()
                bet_in_same_group.success = True
            else:
                bet_in_same_group.success = False
            bet_in_same_group.called_bet = called_bet
            bet_in_same_group.save()

            if created and called_bet == instance:
                models.ScoreLog.objects.create(score=entry.current_score, entry=entry, called_bet=instance)
            else:
                score_log = models.ScoreLog.objects.filter(entry=entry, called_bet=called_bet).first()
                score_log.score = entry.current_score
                score_log.save()

        # 2. Update positions given the new scores
        position = 1
        ordered_entries = models.Entry.objects.order_by('-current_score', 'profile__user__first_name')
        previous_score = ordered_entries[0].current_score
        for i, entry in enumerate(ordered_entries):
            if entry.current_score < previous_score:
                position = i + 1
            entry.current_position = position
            entry.save()
            if created and called_bet == instance:
                models.PositionLog.objects.create(position=position, entry=entry, called_bet=instance)
            else:
                position_log = models.PositionLog.objects.filter(entry=entry, called_bet=called_bet).first()
                position_log.position = position
                position_log.save()
            previous_score = entry.current_score


@receiver(post_save, sender=models.CalledBet)
def updated_called_bets(sender, instance, created, **kwargs):
    recalculate_from_instance(instance, created)


@receiver(post_delete, sender=models.CalledBet)
def removed_from_called_bets(sender, instance, **kwargs):
    recalculate_scores_and_positions_delete(instance)

    # Finally clear the success statuses
    models.Bet.objects.filter(outcome__choice_group=instance.outcome.choice_group).update(success=None)


@receiver(post_save, sender=models.Entry)
def label_entries(sender, instance, created, **kwargs):
    all_entries = instance.profile.entries.order_by('id')
    labels = ["A", "B", "C"]
    if created:
        if len(all_entries) == 1:
            entry = all_entries.first()
            entry.label = None
            entry.save()

        else:
            for entry, label in zip(all_entries, labels):
                entry.label = label
                entry.save()


@receiver(post_delete, sender=models.Entry)
def relabel_entries(sender, instance, **kwargs):
    all_entries = instance.profile.entries.order_by('id')
    labels = ["A", "B", "C"]
    if len(all_entries) == 1:
        entry = all_entries.first()
        entry.label = None
        entry.save()

    else:
        for entry, label in zip(all_entries, labels):
            entry.label = label
            entry.save()
