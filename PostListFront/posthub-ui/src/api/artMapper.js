// src/api/artMappers.js (или как он у тебя называется)

// соответствие: что приходит с бэка → во что превращается на фронте
const API_STATUS_TO_UI = {
    done: "complete",
    in_progress: "in_progress",
    cancelled: "in_progress",
    only_planned: "in_progress",
    waiting_to_start: "in_progress",
}

// и обратное соответствие: фронтовый статус → что отправляем на бэк
const UI_STATUS_TO_API = {
    complete: "done",
    in_progress: "in_progress", // при желании можно будет поменять на "only_planned"
}

export function mapArtFromApi(row) {
    return {
        id: row.id,
        name: row.name,

        // сырой статус с бэка — для логики/отладки
        statusRaw: row.status,
        // нормализованный статус для UI — только "complete" / "in_progress"
        status: API_STATUS_TO_UI[row.status] || "in_progress",

        // человек / фурри — булевы флаги
        human: row.human_type === "yes",
        furry: row.furry_type === "yes",

        // контент
        isNsfw: !!row.is_nsfw,
        isSfw: !!row.is_sfw,
        isNsfwPlusCrop: !!row.is_nsfw_plus_crop,

        price: row.price ?? 0,
        locked: !!row.locked,

        // куда планируем постить
        postOnBsky: !!row.post_on_bsky,
        postOnLewdTwi: !!row.post_on_lewd_twi,
        postOnDecentTwi: !!row.post_on_decent_twi,

        // статусы по площадкам пока оставляем как есть (строки enum'а)
        bskyPosted: row.bsky_posted,
        lewdTwiPosted: row.lewd_twi_posted,
        decentTwiPosted: row.decent_twi_posted,

        createdAt: row.created_at,
        updatedAt: row.updated_at,
    }
}

export function mapArtToApi(art) {
    return {
        name: art.name,

        // UI → API: возвращаемся в мир бекенд-статусов
        // если вдруг status не в словаре — откатываемся к исходному statusRaw
        status: UI_STATUS_TO_API[art.status] || art.statusRaw || "in_progress",

        human_type: art.human ? "yes" : "no",
        furry_type: art.furry ? "yes" : "no",

        is_nsfw: !!art.isNsfw,
        is_sfw: !!art.isSfw,
        is_nsfw_plus_crop: !!art.isNsfwPlusCrop,

        price: art.price ?? 0,
        locked: !!art.locked,

        post_on_bsky: !!art.postOnBsky,
        post_on_lewd_twi: !!art.postOnLewdTwi,
        post_on_decent_twi: !!art.postOnDecentTwi,

        // статусы площадок — как есть (enum из бэка)
        bsky_posted: art.bskyPosted,
        lewd_twi_posted: art.lewdTwiPosted,
        decent_twi_posted: art.decentTwiPosted,
    }
}
