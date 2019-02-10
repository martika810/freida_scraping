from src.progress import Progress

def test_read_total_number_items():

    progress = Progress()
    progress.init()
    total_number_items = progress.read_total_number_items()
    assert total_number_items == 0


def test_save_number_items_scraped_so_far():
    progress = Progress()
    progress.init()
    total_number_items = progress.read_total_number_items()
    items_scraped_so_far = progress.read_number_items_scraped_so_far()
    assert total_number_items == 0
    assert items_scraped_so_far == 0

    progress.save_number_items_scraped_so_far(10)
    progress.save_total_number_items(5)
    items_scraped_so_far = progress.read_number_items_scraped_so_far()
    total_number_items = progress.read_total_number_items()
    assert items_scraped_so_far == 10
    assert total_number_items

def test_add_item_scraped():
    progress = Progress()
    progress.init()
    progress_result = progress.read_progress()
    assert progress_result['items_scraped'] == 0
    assert progress_result['total'] == 0
    assert len(progress_result['items']) == 0

    some_object = {
         'property' : 'value'
    }
    progress.add_item_scraped(some_object)
    progress_result = progress.read_progress()
    assert len(progress_result['items']) == 1