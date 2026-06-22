from sqlmodel import Session


class BaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, instance):
        self.session.add(instance)
        return instance

    def delete(self, instance) -> None:
        self.session.delete(instance)

    def get(self, model, instance_id):
        return self.session.get(model, instance_id)
