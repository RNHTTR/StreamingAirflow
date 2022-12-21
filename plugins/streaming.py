from datetime import timedelta, datetime

from airflow.models import DagRun
from airflow.plugins_manager import AirflowPlugin
# from airflow.utils.session import create_session
from airflow.settings import Session
from airflow.timetables.base import DagRunInfo, DataInterval, TimeRestriction, Timetable
from pendulum import instance, now, UTC, DateTime


class StreamingTimetable(Timetable):
    """
    Custom Timetable to ensure a DAG is constantly running,
    allowing for KubernetesPodOperatorAsync to run streaming
    jobs in perpetuity.
    """
    def __init__(self, dag_id: str) -> None:
        self._dag_id = dag_id

    def serialize(self) -> dict[str, str]:
        return {"dag_id": self._dag_id}

    @classmethod
    def deserialize(cls, value: dict[str, str]) -> Timetable:
        return cls(value["dag_id"])

    def infer_manual_data_interval(self, run_after: DateTime) -> DataInterval:
        return DataInterval(
            start=run_after, 
            end=instance(datetime.fromordinal(run_after.date().toordinal())).add(days=1)
        )

    def next_dagrun_info(
        self,
        *,
        last_automated_data_interval: DataInterval,
        restriction: TimeRestriction,
    ) -> DagRunInfo:
        current_time = now('UTC')
        midnight_today = instance(datetime.fromordinal(current_time.date().toordinal()))

        if not last_automated_data_interval:
            return DagRunInfo.interval(
                    start=midnight_today.subtract(days=1),
                    end=midnight_today
                )
        else:
            session = Session()
            dr = session.query(DagRun).filter(DagRun.dag_id == self._dag_id).one()
            if dr.state == "running":
                # DataInterval should start tomorrw midnight and end the following midnight
                info = DagRunInfo.interval(
                    start=midnight_today,
                    end=midnight_today.add(days=1)
                )
            else:
                # DataInterval should restart today midnight and end tomorrow midnight
                # XXX Can DAGs have different DataIntervals? I think that'd break things.
                info = DagRunInfo.interval(
                    # start=midnight_today,
                    # end=(midnight_today + timedelta(days=1))
                    start=current_time,
                    end=midnight_today
                )
        return info


class StreamingTimetablePlugin(AirflowPlugin):
    name = "streaming_timetable_plugin"
    timetables = [StreamingTimetable]