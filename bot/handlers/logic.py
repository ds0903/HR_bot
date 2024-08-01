import aiosqlite

datab2 = "hr_bot.db"


# datab2 = "/home/ubuntu/hr_bot.db"
async def create_history(user_id, posada, misto, zarplata_ot, zarplata_do, dosvid):

    async with aiosqlite.connect(datab2) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO search_history (user_id, posada, misto, zarplata_ot, zarplata_do, dosvid) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    posada,
                    misto,
                    zarplata_ot,
                    zarplata_do,
                    dosvid,
                ),
            )
            await conn.commit()


async def search_history(
    user_id,
):
    async with aiosqlite.connect(datab2) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM search_history WHERE user_id = ?", (user_id,)
            )
            results = await cursor.fetchall()
            return results


async def delete_history(user_id):
    async with aiosqlite.connect(datab2) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM search_history WHERE user_id = ?", (user_id,)
            )
            await conn.commit()
