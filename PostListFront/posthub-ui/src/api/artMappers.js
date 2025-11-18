// src/api/artMapper.js

// Нормализация статуса из API во внутренний формат UI
export function normalizeStatusFromApi(apiStatus) {
    if (!apiStatus) return 'only_planned'

    switch (apiStatus) {
        case 'done':
            return 'complete'
        case 'in_progress':
            return 'in_progress'
        case 'cancelled':
            return 'cancelled'
        case 'only_planned':
            return 'only_planned'
        case 'waiting_to_start':
            return 'waiting_to_start'
        default:
            return apiStatus
    }
}

// Обратная нормализация: из UI в то, что ждёт Django
export function normalizeStatusToApi(uiStatus) {
    if (!uiStatus) return 'only_planned'

    switch (uiStatus) {
        case 'complete':
            return 'done'
        case 'in_progress':
            return 'in_progress'
        case 'cancelled':
            return 'cancelled'
        case 'only_planned':
            return 'only_planned'
        case 'waiting_to_start':
            return 'waiting_to_start'
        default:
            return uiStatus
    }
}

// Из API → во внутренний формат, с которым работает RightPanel
export function mapArtFromApi(row) {
    const art = {}

    art.id = row.id
    art.name = row.name || ''

    // статус: конверсия done -> complete
    if (row.status === 'done') {
        art.status = 'complete'
    } else {
        art.status = 'in_progress'
    }

    // человек / фурри
    art.human = row.human_type === 'yes'
    art.furry = row.furry_type === 'yes'

    // контент
    art.sfw = Boolean(row.is_sfw)
    art.nsfw = Boolean(row.is_nsfw)
    art.crop = Boolean(row.is_nsfw_plus_crop)

    // куда постить
    art.post_targets = {
        twi16: Boolean(row.post_on_decent_twi),
        twi18: Boolean(row.post_on_lewd_twi),
        bsky:  Boolean(row.post_on_bsky),
    }

    // что выложено
    art.posted = {
        twi16: row.decent_twi_posted === 'posted',
        twi18: row.lewd_twi_posted === 'posted',
        bsky:  row.bsky_posted === 'posted',
    }

    art.locked = Boolean(row.locked)
    art.price = row.price ?? 0

    art.createdAt = row.created_at
    art.updatedAt = row.updated_at

    return art
}


// Из внутреннего формата UI → в JSON тела запроса к API
export function mapArtToApi(art) {
    const payload = {}

    payload.name = art.name

    // конверсия статуса
    if (art.status === 'complete') {
        payload.status = 'done'
    } else {
        payload.status = 'in_progress'
    }

    payload.human_type = art.human ? 'yes' : 'no'
    payload.furry_type = art.furry ? 'yes' : 'no'

    payload.is_sfw = Boolean(art.sfw)
    payload.is_nsfw = Boolean(art.nsfw)
    payload.is_nsfw_plus_crop = Boolean(art.crop)

    payload.post_on_decent_twi = Boolean(art.post_targets.twi16)
    payload.post_on_lewd_twi   = Boolean(art.post_targets.twi18)
    payload.post_on_bsky       = Boolean(art.post_targets.bsky)

    if (art.posted.twi16) {
        payload.decent_twi_posted = 'posted'
    } else {
        payload.decent_twi_posted = 'not_posted'
    }

    if (art.posted.twi18) {
        payload.lewd_twi_posted = 'posted'
    } else {
        payload.lewd_twi_posted = 'not_posted'
    }

    if (art.posted.bsky) {
        payload.bsky_posted = 'posted'
    } else {
        payload.bsky_posted = 'not_posted'
    }

    payload.locked = Boolean(art.locked)
    payload.price = art.price ?? 0

    return payload
}

