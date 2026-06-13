from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from .models import Attraction
from django.db.models import Q, Count, Avg, Func
import requests
import json
import random
import os
import markdown

# ========== 首页视图 ==========
def index(request):
    total_attractions = Attraction.objects.count()
    total_provinces = Attraction.objects.values('province').distinct().exclude(province__isnull=True).exclude(province='').count()
    total_cities = Attraction.objects.exclude(city__isnull=True).exclude(city='').values('city').distinct().count()
    high_rated = Attraction.objects.filter(rating__gte=4.5).count()

    hot_provinces = list(Attraction.objects.values('province')
                         .exclude(province__isnull=True).exclude(province='')
                         .annotate(count=Count('id'))
                         .order_by('-count')[:10])

    # 热门景点（过滤红色文化）
    red_keywords = ['纪念馆', '故居', '烈士陵园', '烈士', '红军', '革命', '抗战', '抗日', '起义', '会议会址', '办事处', '纪念园', '陵园']
    all_rated = list(Attraction.objects.exclude(rating__isnull=True).filter(rating__gte=4.5).order_by('-rating')[:100])
    scenic_spots = [a for a in all_rated if not any(kw in a.name for kw in red_keywords)]
    red_spots = [a for a in all_rated if any(kw in a.name for kw in red_keywords)]
    random.shuffle(scenic_spots)
    hot_attractions_list = scenic_spots[:5]
    remaining = scenic_spots[5:] + red_spots
    random.shuffle(remaining)
    hot_attractions_list.extend(remaining[:3])
    random.shuffle(hot_attractions_list)
    hot_attractions_list = hot_attractions_list[:8]

    # 类型统计
    type_counts = {}
    for attr in Attraction.objects.exclude(type__isnull=True).exclude(type='').iterator(chunk_size=2000):
        parts = attr.type.split(';')
        category = parts[-1] if len(parts) >= 3 else (parts[-1] if parts else '其他')
        merge_map = {
            '风景名胜': '自然风光', '旅游景点': '旅游景点',
            '公园': '公园广场', '公园广场': '公园广场', '城市广场': '公园广场',
            '寺庙道观': '宗教文化', '教堂': '宗教文化', '回教寺': '宗教文化',
            '纪念馆': '文化场馆', '国家级景点': '国家级景区', '省级景点': '省级景区',
            '观景点': '观光景点', '植物园': '动植物园', '动物园': '动植物园',
            '水族馆': '动植物园', '海滩': '海滨度假', '红色景区': '红色旅游',
            '陵园': '纪念场所', '游乐场': '主题乐园',
        }
        category = merge_map.get(category, category)
        type_counts[category] = type_counts.get(category, 0) + 1
    sorted_types = sorted(type_counts.items(), key=lambda x: -x[1])
    type_stats = [{'name': name, 'value': count} for name, count in sorted_types[:7]]
    if len(sorted_types) > 7:
        others = sum(c for _, c in sorted_types[7:])
        if others > 0:
            type_stats.append({'name': '其他', 'value': others})

    # 图片墙
    all_with_photos = list(Attraction.objects.filter(rating__gte=4.5).exclude(photos__isnull=True).exclude(photos=''))
    scenic_photos = [a for a in all_with_photos if not any(kw in a.name for kw in red_keywords)]
    red_photos = [a for a in all_with_photos if any(kw in a.name for kw in red_keywords)]
    random.shuffle(scenic_photos)
    random.shuffle(red_photos)
    rated_photos = scenic_photos[:15] + red_photos[:5]
    random_photos = list(Attraction.objects.exclude(photos__isnull=True).exclude(photos='').order_by('?')[:20])

    def extract_image(attr):
        try:
            if attr.photos.startswith('['):
                photos = json.loads(attr.photos)
                if photos:
                    return photos[0] if isinstance(photos[0], str) else photos[0].get('url', '')
            elif attr.photos.startswith('http'):
                return attr.photos
        except:
            pass
        return None

    image_wall, seen = [], set()
    for attr in rated_photos:
        if attr.id in seen: continue
        img = extract_image(attr)
        if img:
            image_wall.append({'name': attr.name, 'city': attr.city or '', 'province': attr.province or '', 'image': img, 'rating': attr.rating})
            seen.add(attr.id)
    for attr in random_photos:
        if len(image_wall) >= 8: break
        if attr.id in seen: continue
        img = extract_image(attr)
        if img:
            image_wall.append({'name': attr.name, 'city': attr.city or '', 'province': attr.province or '', 'image': img, 'rating': attr.rating or '-'})
            seen.add(attr.id)
    random.shuffle(image_wall)

    # 地图数据
    all_provinces = list(Attraction.objects.values('province').exclude(province__isnull=True).exclude(province='').annotate(count=Count('id')))
    province_count_map = {p['province']: p['count'] for p in all_provinces}
    echarts_full_names = [
        '北京市', '天津市', '上海市', '重庆市',
        '河北省', '山西省', '辽宁省', '吉林省', '黑龙江省',
        '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省',
        '河南省', '湖北省', '湖南省', '广东省', '海南省',
        '四川省', '贵州省', '云南省', '陕西省', '甘肃省', '青海省', '台湾省',
        '内蒙古自治区', '广西壮族自治区', '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区',
        '香港特别行政区', '澳门特别行政区'
    ]
    map_data = [{'name': name, 'value': province_count_map.get(name, 0)} for name in echarts_full_names]

    context = {
        'total_attractions': total_attractions,
        'total_provinces': total_provinces,
        'total_cities': total_cities,
        'high_rated': high_rated,
        'hot_provinces': hot_provinces,
        'hot_attractions_list': hot_attractions_list,
        'type_stats': type_stats,
        'image_wall': image_wall,
        'map_data': map_data,
    }
    return render(request, 'attractions/index.html', context)


# ========== 搜索视图 ==========
def search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Attraction.objects.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(province__icontains=query) |
            Q(address__icontains=query)
        )[:50]
    return render(request, 'attractions/search.html', {
        'query': query,
        'results': results,
        'count': len(results)
    })


# ========== 省份详情视图 ==========
def province_detail(request, province_name):
    cities = Attraction.objects.filter(province=province_name).values('city').distinct()
    if not cities:
        for suffix in ['省', '市', '自治区', '特别行政区']:
            test_name = province_name + suffix
            cities = Attraction.objects.filter(province=test_name).values('city').distinct()
            if cities:
                province_name = test_name
                break
    if not cities:
        base_name = province_name.replace('省', '').replace('市', '').replace('自治区', '').replace('特别行政区', '')
        cities = Attraction.objects.filter(province__contains=base_name).values('city').distinct()
        if cities:
            actual = Attraction.objects.filter(province__contains=base_name).first()
            if actual:
                province_name = actual.province

    city_list = []
    for c in cities:
        city_name = c['city']
        if not city_name:
            continue
        top_attr = Attraction.objects.filter(city=city_name).exclude(photos__isnull=True).exclude(photos='').order_by('-rating').first()
        city_img = ''
        if top_attr:
            try:
                photos = json.loads(top_attr.photos) if top_attr.photos.startswith('[') else []
                if photos:
                    city_img = photos[0] if isinstance(photos[0], str) else photos[0].get('url', '')
            except:
                pass
        city_count = Attraction.objects.filter(city=city_name).count()
        city_list.append({'name': city_name, 'count': city_count, 'image': city_img})

    return render(request, 'attractions/province_detail.html', {
        'province': province_name,
        'city_list': city_list,
    })


# ========== 城市详情视图 ==========
def city_detail(request, city_name):
    attractions = Attraction.objects.filter(city=city_name)
    if not attractions:
        attractions = Attraction.objects.filter(city=city_name + '市')
        if attractions:
            city_name = city_name + '市'

    for attr in attractions:
        attr.image_url = ''
        if attr.photos:
            try:
                if attr.photos.startswith('['):
                    photos = json.loads(attr.photos)
                    if photos:
                        attr.image_url = photos[0] if isinstance(photos[0], str) else photos[0].get('url', '')
                elif attr.photos.startswith('http'):
                    attr.image_url = attr.photos
            except:
                pass

    return render(request, 'attractions/city_detail.html', {
        'city': city_name,
        'attractions': attractions,
    })


# ========== AI 聊天视图（支持 AJAX） ==========
@csrf_exempt
def ai_chat(request):
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if not question:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': '问题不能为空'}, status=400)
            return render(request, 'attractions/ai_chat.html', {'error': '问题不能为空'})

        answer = call_ai_api(question)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'question': question, 'answer': answer})
        else:
            return render(request, 'attractions/ai_chat.html', {
                'question': question,
                'answer': answer,
            })

    return render(request, 'attractions/ai_chat.html')


# ========== 本地景点检索函数 ==========
def search_local_attractions(question):
    # 常见城市列表（可动态从数据库获取）
    cities = ['北京', '上海', '广州', '深圳', '成都', '杭州', '西安', '南京', '武汉', '重庆', '厦门', '青岛', '大连', '苏州', '长沙', '昆明', '贵阳']
    city = None
    for c in cities:
        if c in question:
            city = c
            break
    if not city:
        return None, "未检测到具体城市，我将根据通用知识回答。"

    attractions = Attraction.objects.filter(city__contains=city).exclude(rating__isnull=True).order_by('-rating')[:8]
    if not attractions:
        return city, f"数据库中暂无 {city} 的景点数据。"

    lines = [f"根据本地数据库，{city} 有以下热门景点（评分由高到低）："]
    for idx, a in enumerate(attractions, 1):
        rating = a.rating if a.rating else '暂无评分'
        lines.append(f"{idx}. {a.name}（{rating}星）")
    context = "\n".join(lines)
    return city, context


# ========== 调用 DeepSeek API 核心函数 ==========
def call_ai_api(question):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return "❌ 未找到 DeepSeek API Key，请检查项目根目录下的 .env 文件是否配置正确。"

    # 检索本地数据
    city, local_context = search_local_attractions(question)

    system_prompt = """你是一个专业的中国旅游顾问，回答需要实用、具体、有趣。如果提供了本地数据库的景点信息，请优先引用这些景点，并可以补充一些额外的小贴士（如交通、门票、开放时间）。"""

    if local_context and not local_context.startswith("未检测到"):
        user_prompt = f"""用户问题：{question}

{local_context}

请基于以上本地数据库信息，回答用户的问题。你可以适当补充其他实用建议，但请优先推荐数据库中的景点。"""
    else:
        user_prompt = f"用户问题：{question}\n\n（本地数据库中暂无相关数据，请根据你的知识回答）"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            # 可选：将 Markdown 渲染为 HTML，但前端也会渲染，这里保留原样
            return answer
        else:
            return f"❌ API 请求失败（状态码 {response.status_code}）：{response.text}"
    except Exception as e:
        return f"⚠️ 网络错误：{str(e)}"
