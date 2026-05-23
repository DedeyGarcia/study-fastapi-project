from math import ceil
from typing import Annotated, Literal
from datetime import date, datetime, timezone
from fastapi import APIRouter, Body, Path, HTTPException, Query
from pydantic import BaseModel
from enum import Enum

router = APIRouter(
    prefix="/api/v1/pedals",
)


class PedalType(str, Enum):
    GAIN = "gain"
    MODULATION = "modulation"
    AMBIENCE = "ambience"
    PITCH = "pitch"
    DYNAMICS = "dynamics"
    OTHER = "other"


class PedalBase(BaseModel):
    name: str
    brand: str
    type: PedalType
    price: float
    acquired_at: date
    img_url: str | None = None


class PedalCreate(PedalBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Keeley Loomer",
                    "brand": "Keeley Electronics",
                    "type": "gain",
                    "price": 299.00,
                    "acquired_at": "2024-06-01",
                    "img_url": "https://guitarhaus.ca/cdn/shop/files/Loomer-Workstation-Fuzz-Reverb-Angle-White-Keeley-Order-Switch-e1524689879106.jpg?v=1702250462&width=713",
                }
            ]
        }
    }


class PedalPatch(BaseModel):
    name: str | None = None
    brand: str | None = None
    type: PedalType | None = None
    price: float | None = None
    acquired_at: date | None = None
    img_url: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "price": 299.00,
                    "img_url": "https://guitarhaus.ca/cdn/shop/files/Loomer-Workstation-Fuzz-Reverb-Angle-White-Keeley-Order-Switch-e1524689879106.jpg?v=1702250462&width=713",
                }
            ]
        }
    }


class Pedal(PedalBase):
    id: int
    created_at: datetime
    updated_at: datetime


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class PedalListResponse(BaseModel):
    data: list[Pedal]
    metadata: PaginationMeta


id_counter = 2

fake_pedal_db: list[Pedal] = [
    Pedal(
        id=1,
        name="Tube Screamer",
        brand="Ibanez",
        type=PedalType.GAIN,
        price=99.99,
        acquired_at="2023-01-15",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        img_url="https://en.wikipedia.org/wiki/Ibanez_Tube_Screamer#/media/File:Ibanez_TS808_Tube_Screamer_(48588080527)_(cropped).jpg",
    ),
    Pedal(
        id=2,
        name="Big Muff",
        brand="Electro Harmonix",
        type=PedalType.GAIN,
        price=99.99,
        acquired_at="2024-01-15",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        img_url="https://m.media-amazon.com/images/I/71WB-ME9mOL.jpg",
    ),
]


@router.get("/", response_model=PedalListResponse)
async def get_pedals():
    return {"data": fake_pedal_db}


# Paginated Version Option
# async def get_pedals(
#     page: Annotated[int, Query(title="The page number to retrieve", ge=1)] = 1,
#     page_size: Annotated[
#         int, Query(title="The number of items per page", ge=1, le=50)
#     ] = 10,
#     sort_by: Annotated[
#         Literal["name", "brand", "type", "price"] | None,
#         Query(),
#     ] = None,
#     order: Annotated[Literal["asc", "desc"], Query()] = None,
# ):
#     pedals = fake_pedal_db

#     if sort_by is not None:
#         if order is None:
#             raise HTTPException(
#                 status_code=400,
#                 detail="order can only be used when sort_by is provided",
#             )

#         sort_options = {
#             "name": lambda pedal: pedal.name,
#             "brand": lambda pedal: pedal.brand,
#             "type": lambda pedal: pedal.type,
#             "price": lambda pedal: pedal.price,
#         }

#         pedals = sorted(
#             pedals,
#             key=sort_options[sort_by],
#             reverse=(order == "desc"),
#         )

#     total_items = len(pedals)
#     start_index = (page - 1) * page_size
#     end_index = start_index + page_size
#     paginated_pedals = pedals[start_index:end_index]
#     total_pages = ceil(total_items / page_size)
#     return {
#         "data": paginated_pedals,
#         "metadata": {
#             "page": page,
#             "page_size": page_size,
#             "total_items": total_items,
#             "total_pages": total_pages,
#         },
#     }


@router.get("/{pedal_id}")
async def get_pedal(
    pedal_id: Annotated[int, Path(title="The ID of the pedal to retrieve")],
):
    pedal = next((item for item in fake_pedal_db if item.id == pedal_id), None)
    if pedal is None:
        raise HTTPException(status_code=404, detail="Pedal not found")
    return pedal


@router.post("/")
async def create_pedal(pedal_data: Annotated[PedalCreate, Body()]):
    global id_counter
    id_counter += 1
    new_pedal = Pedal(
        id=id_counter,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        **pedal_data.model_dump(),
    )
    fake_pedal_db.append(new_pedal)
    return new_pedal


@router.delete("/{pedal_id}")
async def delete_pedal(
    pedal_id: Annotated[int, Path(title="The ID of the pedal to delete")],
):
    pedal = next((item for item in fake_pedal_db if item.id == pedal_id), None)
    if pedal is None:
        raise HTTPException(status_code=404, detail="Pedal not found")
    fake_pedal_db.remove(pedal)
    return {"message": "Pedal deleted successfully"}


@router.patch("/{pedal_id}")
async def update_pedal(
    pedal_id: Annotated[int, Path(title="The ID of the pedal to update")],
    data_to_be_patched: Annotated[PedalPatch, Body()],
):
    pedal_to_update = next(
        (item for item in fake_pedal_db if item.id == pedal_id), None
    )

    if pedal_to_update is None:
        raise HTTPException(status_code=404, detail="Pedal not found")

    # Change the update strategy from this point down.
    update_data = data_to_be_patched.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(pedal_to_update, field, value)

    pedal_to_update.updated_at = datetime.now(timezone.utc)

    # Alternative 1: create a copy with Pydantic and replace it in the list.
    # pedal_index = fake_pedal_db.index(pedal_to_update)
    # update_data = data_to_be_patched.model_dump(exclude_unset=True)
    # update_data["updated_at"] = datetime.now(timezone.utc)
    # updated_pedal = pedal_to_update.model_copy(update=update_data)
    # fake_pedal_db[pedal_index] = updated_pedal
    # return {"pedal": updated_pedal}

    # Alternative 2: rebuild the full Pydantic model and replace it in the list.
    # pedal_index = fake_pedal_db.index(pedal_to_update)
    # updated_pedal_data = {
    #     **pedal_to_update.model_dump(),
    #     **data_to_be_patched.model_dump(exclude_unset=True),
    #     "updated_at": datetime.now(timezone.utc),
    # }
    # updated_pedal = Pedal(**updated_pedal_data)
    # fake_pedal_db[pedal_index] = updated_pedal
    # return {"pedal": updated_pedal}

    return pedal_to_update
