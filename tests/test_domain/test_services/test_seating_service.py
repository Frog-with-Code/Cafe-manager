import pytest
from uuid import uuid4

from cafe_manager.common.exceptions import ChairError, TableOccupationError, TableError
from cafe_manager.domain.entities.equipment import Table, Chair
from cafe_manager.domain.services.seating_service import SeatingService


class TestSeatingService:

    @pytest.fixture
    def service(self) -> SeatingService:
        return SeatingService()

    @pytest.fixture
    def table_4_places(self) -> Table:
        return Table(max_places=4)

    @pytest.fixture
    def table_2_places(self) -> Table:
        return Table(max_places=2)

    @pytest.fixture
    def free_chair(self) -> Chair:
        return Chair()

    def test_validate_negative_people_amount(self, service, table_4_places, free_chair):
        with pytest.raises(ValueError, match=f"Value {-1} must be positive"):
            service.reserve(
                people_amount=-1, tables=[table_4_places], free_chairs=[free_chair]
            )

    def test_reserve_no_available_tables(self, service, table_4_places, free_chair):
        free_chair.assign_to_table(table_4_places.table_id)
        table_4_places.add_chair(free_chair.chair_id)
        table_4_places.occupy(1)

        with pytest.raises(TableOccupationError, match="No free tables"):
            service.reserve(
                tables=[table_4_places], free_chairs=[free_chair], people_amount=2
            )

    def test_reserve_no_table_with_enough_places(
        self, service, table_2_places, free_chair
    ):
        with pytest.raises(
            TableOccupationError, match="No available table for 3 people"
        ):
            service.reserve(
                tables=[table_2_places], free_chairs=[free_chair] * 3, people_amount=3
            )

    def test_reserve_not_enough_total_chairs_in_cafe(
        self, service, table_4_places, free_chair
    ):
        with pytest.raises(
            TableOccupationError, match="Not enough chairs for 2 people"
        ):
            service.reserve(
                tables=[table_4_places], free_chairs=[free_chair], people_amount=2
            )

    def test_reserve_direct_candidate_no_dislocation(self, service, table_4_places):
        chair1, chair2 = Chair(), Chair()
        chair1.assign_to_table(table_4_places.table_id)
        chair2.assign_to_table(table_4_places.table_id)
        table_4_places.add_chair(chair1.chair_id)
        table_4_places.add_chair(chair2.chair_id)

        free_chairs = [chair1, chair2]

        occupied_table, _, updated_chairs = service.reserve(
            tables=[table_4_places], free_chairs=free_chairs, people_amount=2
        )

        assert occupied_table == table_4_places
        assert not occupied_table.is_available

        assert chair1.can_be_occupied() is False
        assert chair2.can_be_occupied() is False
        assert table_4_places.chairs_amount == 2

    def test_reserve_with_chair_dislocation(
        self, service, table_4_places, table_2_places
    ):
        chair_on_other_table = Chair()
        chair_on_other_table.assign_to_table(table_2_places.table_id)
        table_2_places.add_chair(chair_on_other_table.chair_id)

        free_chair = Chair()

        tables = [table_4_places, table_2_places]
        free_chairs = [chair_on_other_table, free_chair]

        occupied_table, updated_tables, updated_chairs = service.reserve(
            tables=tables, free_chairs=free_chairs, people_amount=2
        )

        assert table_4_places.chairs_amount == 0
        assert table_2_places.chairs_amount == 2

        assert free_chair.table_id == table_2_places.table_id
        assert chair_on_other_table.table_id == table_2_places.table_id

        assert occupied_table == table_2_places
        assert occupied_table.is_available is False
        assert free_chair.can_be_occupied() is False
        assert chair_on_other_table.can_be_occupied() is False

    def test_free_success(self, service, table_4_places):
        chair1, chair2 = Chair(), Chair()

        chair1.assign_to_table(table_4_places.table_id)
        chair2.assign_to_table(table_4_places.table_id)
        table_4_places.add_chair(chair1.chair_id)
        table_4_places.add_chair(chair2.chair_id)

        service.reserve(
            tables=[table_4_places], free_chairs=[chair1, chair2], people_amount=2
        )

        freed_table, updated_chairs = service.free(
            occupied_tables=[table_4_places],
            occupied_chairs=[chair1, chair2],
            table_id=table_4_places.table_id,
        )

        assert freed_table == table_4_places

        assert freed_table.is_available is False

        assert chair1.can_be_occupied() is True
        assert chair2.can_be_occupied() is True

    def test_free_table_not_found(self, service, table_4_places):
        with pytest.raises(TableError, match="No occupied table with id"):
            service.free(
                occupied_tables=[table_4_places], occupied_chairs=[], table_id=uuid4()
            )

    def test_free_preserves_other_tables_chairs(
        self, service, table_4_places, table_2_places
    ):
        chair_target = Chair()
        chair_target.assign_to_table(table_4_places.table_id)
        table_4_places.add_chair(chair_target.chair_id)
        chair_target.occupy()

        table_4_places._state = table_4_places._state.OCCUPIED

        chair_other = Chair()
        chair_other.assign_to_table(table_2_places.table_id)
        table_2_places.add_chair(chair_other.chair_id)
        chair_other.occupy()
        table_2_places._state = table_2_places._state.OCCUPIED

        freed_table, updated_chairs = service.free(
            occupied_tables=[table_4_places, table_2_places],
            occupied_chairs=[chair_target, chair_other],
            table_id=table_4_places.table_id,
        )

        assert freed_table == table_4_places

        assert chair_target.can_be_occupied() is True

        assert chair_other.can_be_occupied() is False

    def test_dislocate_chairs_not_enough_free_chairs(self, service, table_4_places):
        chair1, chair2 = Chair(), Chair()

        with pytest.raises(
            ChairError, match="Not enough free chairs to fill the table"
        ):
            service._dislocate_chairs(
                free_chairs=[chair1, chair2],
                tables=[table_4_places],
                target_table=table_4_places,
                people_amount=3,
            )

    def test_get_table_by_id_none(self, service, table_4_places):
        result = service._get_table_by_id(tables=[table_4_places], table_id=None)
        assert result is None
